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
    
    # Ensure we have at least 2 rounds for testing auto-advancement
    num_rounds = max(num_rounds, 2)
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
                tournament_id=tournament_id,
                round_number=round_num,
                match_number=match_num,
                player1_id=None,
                player2_id=None,
                winner_id=None,
                next_match_id=None  # We'll set this after all matches are created
            )
            matches.append(match)
            match_id_counter += 1
    
    # Save all matches first so they have proper IDs
    # Important: We use add_all to add all matches at once rather than individually
    # This helps SQLAlchemy optimize the operations and avoid duplicate key errors
    db.session.add_all(matches)
    db.session.flush()  # This assigns IDs without committing the transaction
    
    print(f"Created {len(matches)} matches for tournament {tournament_id}")
    
    # Now connect matches to their next round matches and auto-advance byes
    # First pass: set next_match_id for each match
    for match in matches:
        if match.round_number < num_rounds:
            next_round = match.round_number + 1
            next_match_number = (match.match_number - 1) // 2 + 1
            
            # Find the next match
            for potential_next in matches:
                if (potential_next.round_number == next_round and 
                    potential_next.match_number == next_match_number):
                    match.next_match_id = potential_next.id
                    break
    
    # Second pass: auto-advance bye matches
    for match in matches:
        # If this is a bye match with a winner already set
        if match.winner_id and match.next_match_id:
            next_match = None
            for potential_next in matches:
                if potential_next.id == match.next_match_id:
                    next_match = potential_next
                    break
            
            if next_match:
                # Set the player in next match based on match number
                if match.match_number % 2 == 1:  # Odd match number
                    next_match.player1_id = match.winner_id
                else:  # Even match number
                    next_match.player2_id = match.winner_id
                    
                # If this created a single-player match (other slot is a bye)
                if (next_match.player1_id and not next_match.player2_id) or \
                   (next_match.player2_id and not next_match.player1_id):
                    # Auto-advance this player
                    next_match.winner_id = next_match.player1_id or next_match.player2_id
    
    return matches

def update_match_result(match_id, winner_id):
    """
    Update a match with the winner and propagate the result to the next match
    """
    try:
        # Convert winner_id to integer if it's a string
        if isinstance(winner_id, str) and winner_id.isdigit():
            winner_id = int(winner_id)
        
        match = Match.query.get(match_id)
        if not match:
            print(f"Error: Match {match_id} not found")
            return False
        
        # Validate that winner_id belongs to one of the players in the match
        if not match.player1_id and not match.player2_id:
            print(f"Error: Match {match_id} has no players")
            return False
            
        # If there's a bye (one player is None), the other player automatically wins
        if not match.player1_id:
            if winner_id != match.player2_id:
                print(f"Error: Winner {winner_id} is not player2 {match.player2_id} in a bye match")
                return False
        elif not match.player2_id:
            if winner_id != match.player1_id:
                print(f"Error: Winner {winner_id} is not player1 {match.player1_id} in a bye match")
                return False
        # Regular match with two players
        elif winner_id != match.player1_id and winner_id != match.player2_id:
            print(f"Error: Winner {winner_id} is neither player1 {match.player1_id} nor player2 {match.player2_id}")
            return False
        
        match.winner_id = winner_id
        
        # Propagate winner to next match if there is one
        if match.next_match_id:
            next_match = Match.query.get(match.next_match_id)
            if not next_match:
                print(f"Error: Next match {match.next_match_id} not found")
                return False
            
            # Determine if this player should be player1 or player2 in the next match
            # based on the match number being odd or even
            if match.match_number % 2 == 1:  # Odd match number
                next_match.player1_id = winner_id
            else:  # Even match number
                next_match.player2_id = winner_id
            
            # Always save the next match with the updated player
            db.session.add(next_match)
            
            # Check if this is an auto-bye match
            # We need to identify the match where one player has a bye
            # and immediately advance them to the next round

            # First check: if this is a semi-final match and we've just updated the player1 or player2
            # of the final match, we need to check if the other semi-final has a bye
            if next_match.player1_id is not None and next_match.player2_id is None:
                # If player 2 is empty, and there are no more matches after this one
                # (this is the final), we should auto-advance player 1 as the winner
                if next_match.next_match_id is None:
                    # This is the final match and player 2 is a bye, so player 1 wins
                    next_match.winner_id = next_match.player1_id
                    print(f"Auto-win for player {next_match.player1_id} in final match {next_match.id} due to bye")
                else:
                    # Not the final, so just propagate as normal
                    propagate_auto_advance(next_match, next_match.player1_id)
            elif next_match.player2_id is not None and next_match.player1_id is None:
                # If player 1 is empty, and there are no more matches after this one
                # (this is the final), we should auto-advance player 2 as the winner
                if next_match.next_match_id is None:
                    # This is the final match and player 1 is a bye, so player 2 wins
                    next_match.winner_id = next_match.player2_id
                    print(f"Auto-win for player {next_match.player2_id} in final match {next_match.id} due to bye")
                else:
                    # Not the final, so just propagate as normal
                    propagate_auto_advance(next_match, next_match.player2_id)
                
        # Save the current match
        db.session.add(match)
        db.session.commit()
        
        return True
    except Exception as e:
        print(f"Error updating match result: {str(e)}")
        db.session.rollback()
        return False


def propagate_auto_advance(match, winner_id):
    """
    Recursively advance a player through byes all the way to the final if needed
    """
    # Mark winner in current match
    match.winner_id = winner_id
    print(f"Auto-advancing player {winner_id} in match {match.id} due to bye")
    db.session.add(match)
    
    # If there's a next match, propagate the player
    if match.next_match_id:
        next_match = Match.query.get(match.next_match_id)
        if next_match:
            # Set player in the appropriate position based on current match number
            if match.match_number % 2 == 1:  # Odd match number
                next_match.player1_id = winner_id
            else:  # Even match number
                next_match.player2_id = winner_id
                
            db.session.add(next_match)
            db.session.flush()  # Make sure changes are visible within session
            
            # Check if both players are set in the next match
            if next_match.player1_id is not None and next_match.player2_id is not None:
                # Both players are set, no bye to auto-advance
                return
                
            # If this is the final match, don't propagate further
            next_next_match = Match.query.get(next_match.next_match_id) if next_match.next_match_id else None
            if next_next_match is None:
                # No match after this one, so don't auto-advance further (we're at the final)
                return
                
            # Check if we need to continue auto-advancing in next match (if it's also a bye)
            if next_match.player1_id is not None and next_match.player2_id is None:
                # Player 2 is a bye, so player 1 advances automatically
                propagate_auto_advance(next_match, next_match.player1_id)
            elif next_match.player2_id is not None and next_match.player1_id is None:
                # Player 1 is a bye, so player 2 advances automatically
                propagate_auto_advance(next_match, next_match.player2_id)

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
