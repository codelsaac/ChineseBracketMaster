# Tournament bracket generation logic
import math
import random
from collections import defaultdict
from models import Match, Player
from app import db

def create_tournament_bracket(tournament_id):
    """
    Create a tournament bracket with the following rules:
    1. Separate players from the same school where possible
    2. Distribute seeded players appropriately
    3. Balance 'byes' in the first round only
    
    Returns a list of Match objects
    """
    # Get all players in the tournament
    players = Player.query.filter_by(tournament_id=tournament_id).all()
    
    if not players:
        return []
    
    # Calculate number of rounds and total matches needed
    num_players = len(players)
    num_rounds = math.ceil(math.log2(num_players))
    total_slots = 2 ** num_rounds
    
    # Calculate number of byes needed (empty slots)
    num_byes = total_slots - num_players
    
    # Group players by school for distribution
    schools = defaultdict(list)
    for player in players:
        schools[player.school].append(player)
    
    # Separate seeded and non-seeded players
    seeded_players = [p for p in players if p.is_seeded]
    non_seeded_players = [p for p in players if not p.is_seeded]
    
    # Create first round matches
    matches = []
    player_positions = [None] * total_slots
    
    # 1. Place seeded players strategically
    for i, player in enumerate(seeded_players):
        # Position seeded players in power-of-2 positions (1, 2, 4, 8, etc.)
        # or at the opposite ends of the bracket
        if i < num_rounds:
            pos = 2**i - 1
        else:
            pos = total_slots - 1 - (2**(i % num_rounds) - 1)
        
        player_positions[pos] = player
    
    # 2. Distribute byes evenly
    bye_positions = []
    if num_byes > 0:
        # Create a list of potential positions for byes
        potential_bye_positions = [i for i in range(total_slots) if player_positions[i] is None]
        # Prioritize positions that would balance the bracket
        if num_byes < len(potential_bye_positions):
            bye_positions = random.sample(potential_bye_positions, num_byes)
        else:
            bye_positions = potential_bye_positions
    
    # 3. Distribute remaining players with school separation
    remaining_positions = [i for i in range(total_slots) 
                         if player_positions[i] is None and i not in bye_positions]
    
    # Try to separate players from the same school
    remaining_players = non_seeded_players.copy()
    
    # Initialize a school placement map to keep track of where schools are placed
    school_placements = defaultdict(list)
    
    # First, sort schools by size (largest first) to handle bigger schools first
    sorted_schools = sorted(schools.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Begin distributing non-seeded players
    for school, school_players in sorted_schools:
        # Skip seeded players as they've already been placed
        school_non_seeded = [p for p in school_players if not p.is_seeded]
        
        for player in school_non_seeded:
            if player not in remaining_players:
                continue
                
            remaining_players.remove(player)
            
            # Calculate optimal position to separate from same school
            best_position = None
            max_distance = -1
            
            for pos in remaining_positions:
                if not school_placements[school]:
                    # First player from this school, any position is fine
                    best_position = pos
                    break
                
                # Calculate minimum distance to any player from the same school
                min_distance = min(abs(pos - other_pos) for other_pos in school_placements[school])
                
                if min_distance > max_distance:
                    max_distance = min_distance
                    best_position = pos
            
            if best_position is not None:
                player_positions[best_position] = player
                remaining_positions.remove(best_position)
                school_placements[school].append(best_position)
    
    # Randomly place any remaining players
    random.shuffle(remaining_players)
    for player in remaining_players:
        if not remaining_positions:
            break
        pos = remaining_positions.pop(0)
        player_positions[pos] = player
    
    # Create match objects for the first round
    match_id_counter = 1
    next_round_matches = {}
    
    for i in range(0, total_slots, 2):
        player1 = player_positions[i]
        player2 = player_positions[i+1]
        
        player1_id = player1.id if player1 else None
        player2_id = player2.id if player2 else None
        
        # Create Match object
        match = Match(
            id=match_id_counter,
            tournament_id=tournament_id,
            round_number=1,
            match_number=(i//2) + 1,
            player1_id=player1_id,
            player2_id=player2_id,
            winner_id=None,
            next_match_id=None
        )
        matches.append(match)
        
        # Determine which match this feeds into in the next round
        next_round_match_number = (i//4) + 1
        if next_round_match_number not in next_round_matches:
            next_round_matches[next_round_match_number] = match_id_counter + (total_slots//4) + (i//4)
        
        # Auto-advance if there's a bye
        if player1_id and not player2_id:
            match.winner_id = player1_id
        elif player2_id and not player1_id:
            match.winner_id = player2_id
            
        match_id_counter += 1
    
    # Create matches for subsequent rounds
    for round_num in range(2, num_rounds + 1):
        matches_in_round = 2 ** (num_rounds - round_num)
        
        for match_num in range(1, matches_in_round + 1):
            match = Match(
                id=match_id_counter,
                tournament_id=tournament_id,
                round_number=round_num,
                match_number=match_num,
                player1_id=None,
                player2_id=None,
                winner_id=None,
                next_match_id=None if round_num == num_rounds else match_id_counter + (matches_in_round // 2) + ((match_num - 1) // 2)
            )
            matches.append(match)
            match_id_counter += 1
    
    # Connect first round matches to their next round matches
    for i, match in enumerate(matches):
        if match.round_number == 1:
            next_match_number = (match.match_number - 1) // 2 + 1
            for potential_next in matches:
                if (potential_next.round_number == 2 and 
                    potential_next.match_number == next_match_number):
                    match.next_match_id = potential_next.id
                    break
    
    return matches

def update_match_result(match_id, winner_id):
    """
    Update a match with the winner and propagate the result to the next match
    """
    match = Match.query.get(match_id)
    if not match:
        return False
    
    # Validate that winner_id belongs to one of the players in the match
    if winner_id != match.player1_id and winner_id != match.player2_id:
        return False
    
    match.winner_id = winner_id
    
    # Propagate winner to next match if there is one
    if match.next_match_id:
        next_match = Match.query.get(match.next_match_id)
        
        # Determine if this player should be player1 or player2 in the next match
        # based on the match number being odd or even
        if match.match_number % 2 == 1:  # Odd match number
            next_match.player1_id = winner_id
        else:  # Even match number
            next_match.player2_id = winner_id
            
        db.session.add(next_match)
    
    db.session.add(match)
    db.session.commit()
    
    return True

def get_tournament_bracket(tournament_id):
    """
    Retrieve the tournament bracket structure for visualization
    """
    matches = Match.query.filter_by(tournament_id=tournament_id).order_by(Match.round_number, Match.match_number).all()
    
    # Group matches by round
    rounds = {}
    for match in matches:
        if match.round_number not in rounds:
            rounds[match.round_number] = []
        rounds[match.round_number].append(match.to_dict())
    
    # Get player details for lookup
    players = Player.query.filter_by(tournament_id=tournament_id).all()
    player_map = {player.id: player.to_dict() for player in players}
    
    return {
        'rounds': rounds,
        'players': player_map
    }
