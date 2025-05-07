# Tournament bracket generation logic
import math
import random
import logging
from collections import defaultdict
# Removed SQLAlchemy model imports
# from models import Match, Player
# Removed db import from app, use db_firestore when needed (e.g., in get_tournament_bracket)
from app import db_firestore # Keep this if get_tournament_bracket needs it directly

def create_tournament_bracket(tournament_id: str, players_list: list[dict]) -> list[dict]:
    """
    Create a tournament bracket structure based on input players.
    Rules:
    1. Separate players from the same school where possible.
    2. Distribute seeded players appropriately.
    3. Balance 'byes' in the first round only.

    Args:
        tournament_id (str): The ID of the tournament.
        players_list (list[dict]): List of player dictionaries, each containing
                                   at least 'id' (str), 'school' (str), 'is_seeded' (bool).

    Returns:
        list[dict]: A list of match dictionaries ready to be saved to Firestore.
                    Matches do not contain next_match_id, structure is implicit.
    """
    # Use the provided players_list instead of querying
    # players = Player.query.filter_by(tournament_id=tournament_id).all()
    players = players_list

    if not players:
        return []

    num_players = len(players)
    if num_players < 2:
         logging.warning(f"Tournament {tournament_id} has fewer than 2 players. Cannot generate bracket.")
         return [] # Or raise error

    # Calculate number of rounds and total slots needed
    num_rounds = math.ceil(math.log2(num_players))
    # Ensure we have at least 2 rounds for testing auto-advancement visual/logic if needed
    # num_rounds = max(num_rounds, 2) # Reconsider if this is strictly necessary
    total_slots = 2 ** num_rounds
    num_byes = total_slots - num_players

    logging.info(f"Generating bracket for {num_players} players, {num_rounds} rounds, {total_slots} slots, {num_byes} byes.")

    # Group players by school for distribution
    schools = defaultdict(list)
    for player in players:
        # Ensure player has expected keys
        if not all(k in player for k in ('id', 'school', 'is_seeded', 'name')):
             logging.error(f"Player data missing required keys: {player}")
             # Handle error appropriately, maybe skip player or raise exception
             continue
        schools[player['school']].append(player)

    # Separate seeded and non-seeded players (using dictionary access)
    seeded_players = [p for p in players if p.get('is_seeded', False)]
    non_seeded_players = [p for p in players if not p.get('is_seeded', False)]

    # Create first round structure
    player_positions = [None] * total_slots # Stores player dicts or None (for byes)

    # 1. Place seeded players strategically (modify position calculation slightly)
    # Ensure list index access is safe
    seeded_placements = {}
    # Simplified seeding placement: spread across quarters/halves
    seed_order = [0, total_slots // 2, total_slots // 4, 3 * total_slots // 4]
    seed_order += [i for i in range(total_slots) if i not in seed_order] # Fill remaining

    seeded_players.sort(key=lambda p: p.get('name')) # Consistent order for tie-breaking

    current_seed_idx = 0
    placed_seed_count = 0
    while placed_seed_count < len(seeded_players) and current_seed_idx < len(seed_order):
         pos = seed_order[current_seed_idx]
         if player_positions[pos] is None:
             player_positions[pos] = seeded_players[placed_seed_count]
             seeded_placements[pos] = seeded_players[placed_seed_count]
             placed_seed_count += 1
         current_seed_idx += 1

    # Handle cases where seeded players couldn't fit in ideal spots (shouldn't happen if logic is right)
    if placed_seed_count < len(seeded_players):
        logging.warning("Could not place all seeded players optimally, placing remaining randomly.")
        remaining_seeds = seeded_players[placed_seed_count:]
        empty_slots_for_seed = [i for i, p in enumerate(player_positions) if p is None]
        random.shuffle(empty_slots_for_seed)
        for i, player in enumerate(remaining_seeds):
            if i < len(empty_slots_for_seed):
                pos = empty_slots_for_seed[i]
                player_positions[pos] = player
                seeded_placements[pos] = player
            else:
                 logging.error("Ran out of slots placing remaining seeds.") # Should not happen
                 break

    # 2. Distribute byes evenly (Place None)
    # Place byes preferably against lower seeds or spread out
    bye_positions_filled = 0
    # Try placing against seeds first, starting from lowest if possible
    bye_placement_order = sorted(seeded_placements.keys(), reverse=True) # Try opposite lowest seeds
    for seed_pos in bye_placement_order:
        if bye_positions_filled >= num_byes: break
        # Find adjacent slot
        adj_pos = seed_pos + 1 if seed_pos % 2 == 0 else seed_pos - 1
        if 0 <= adj_pos < total_slots and player_positions[adj_pos] is None:
            player_positions[adj_pos] = None # Place Bye (represented by None)
            bye_positions_filled += 1

    # Fill remaining byes in other available slots
    if bye_positions_filled < num_byes:
        available_slots_for_byes = [i for i, p in enumerate(player_positions) if p is None]
        random.shuffle(available_slots_for_byes)
        needed = num_byes - bye_positions_filled
        for i in range(min(needed, len(available_slots_for_byes))):
             player_positions[available_slots_for_byes[i]] = None
             bye_positions_filled += 1

    # 3. Distribute remaining non-seeded players with school separation
    available_slots = [i for i, p in enumerate(player_positions) if p is None]
    school_placements = defaultdict(list)
    # Add seeded player positions to school_placements for separation logic
    for pos, player in seeded_placements.items():
        school_placements[player['school']].append(pos)

    # Sort schools by size (largest first) to handle bigger schools first
    sorted_schools = sorted(schools.items(), key=lambda item: len([p for p in item[1] if not p.get('is_seeded')]), reverse=True)

    players_to_place = non_seeded_players.copy()
    random.shuffle(players_to_place) # Randomize order within non-seeded

    placed_count = 0
    for player in players_to_place:
        best_pos = -1
        max_min_dist = -1

        current_school = player['school']
        occupied_by_school = school_placements[current_school]

        if not occupied_by_school:
            # First player from this school, try random available slot
             if available_slots:
                  best_pos = random.choice(available_slots)
        else:
            # Find slot furthest from others of the same school
            for slot in available_slots:
                # Calculate min distance to any player from the same school in the bracket circle
                min_dist = float('inf')
                for placed_pos in occupied_by_school:
                     # Distance considering wrap-around might be better, but simple diff for now
                     dist = abs(slot - placed_pos)
                     # Alternative: dist = min(abs(slot - placed_pos), total_slots - abs(slot - placed_pos))
                     min_dist = min(min_dist, dist)

                if min_dist > max_min_dist:
                     max_min_dist = min_dist
                     best_pos = slot
                elif min_dist == max_min_dist:
                     # Tie-break randomly or prefer lower index?
                     if best_pos == -1 or random.random() < 0.5:
                          best_pos = slot

        # Fallback if no best_pos found (e.g., only one slot left)
        if best_pos == -1 and available_slots:
             best_pos = random.choice(available_slots)

        if best_pos != -1:
             player_positions[best_pos] = player
             school_placements[current_school].append(best_pos)
             available_slots.remove(best_pos)
             placed_count += 1
        else:
             logging.error(f"Could not find position for player {player['id']} from {player['school']} - available slots: {len(available_slots)}")
             # This shouldn't happen if logic is correct

    # Final check if all slots are filled (except expected byes)
    filled_slots = sum(1 for p in player_positions if p is not None)
    if filled_slots != num_players:
        logging.error(f"Mismatch in placed players: Expected {num_players}, Got {filled_slots}")

    # --- Create Match Dictionaries --- 
    matches_data = []
    round1_matches_count = total_slots // 2

    # Create match dictionaries for the first round
    for i in range(round1_matches_count):
        pos1 = i * 2
        pos2 = i * 2 + 1
        player1_dict = player_positions[pos1]
        player2_dict = player_positions[pos2]

        player1_id = player1_dict['id'] if player1_dict else None
        player2_id = player2_dict['id'] if player2_dict else None

        winner_id = None
        match_status = 'pending'
        # Auto-advance if there's a bye
        if player1_id and not player2_id:
            winner_id = player1_id
            match_status = 'completed'
        elif player2_id and not player1_id:
            winner_id = player2_id
            match_status = 'completed'
        elif not player1_id and not player2_id:
            # This shouldn't happen with correct bye logic, but handle defensively
            logging.warning(f"Match {i+1} in round 1 has two byes.")
            match_status = 'completed' # Or maybe 'invalid'

        match_dict = {
            'tournament_id': tournament_id,
            'round_number': 1,
            'match_number': i + 1, # 1-based index within the round
            'player1_id': player1_id, # Store ID (string)
            'player2_id': player2_id, # Store ID (string)
            'winner_id': winner_id,  # Store ID (string) or None
            # 'next_match_id': None, # Will be populated later
            'next_match_index': None, # Placeholder for linking before IDs exist
            'status': match_status # pending, completed
        }
        matches_data.append(match_dict)

    # Create placeholder match dictionaries for subsequent rounds
    match_counter_in_round = 0
    matches_in_prev_round = round1_matches_count
    for round_num in range(2, num_rounds + 1):
        matches_in_round = matches_in_prev_round // 2
        for i in range(matches_in_round):
             match_dict = {
                'tournament_id': tournament_id,
                'round_number': round_num,
                'match_number': i + 1,
                'player1_id': None,
                'player2_id': None,
                'winner_id': None,
                # 'next_match_id': None, # Will be populated later
                'next_match_index': None, # Placeholder for linking before IDs exist
                'status': 'pending' # Initially pending until players advance
            }
             matches_data.append(match_dict)
        matches_in_prev_round = matches_in_round

    # Removed database saving logic (db.session.add_all, flush, etc.)
    # Removed logic that linked matches using next_match_id based on DB IDs
    # --- Link matches using indices (before Firestore IDs exist) ---
    match_index_map = {(m['round_number'], m['match_number']): i for i, m in enumerate(matches_data)}

    for i, match in enumerate(matches_data):
        current_round = match['round_number']
        current_match_num = match['match_number']

        if current_round < num_rounds: # Not the final round
            next_round = current_round + 1
            # The winner of match 'k' in round 'r' goes to match ceil(k/2) in round 'r+1'
            next_match_num = math.ceil(current_match_num / 2)
            next_match_key = (next_round, next_match_num)

            if next_match_key in match_index_map:
                matches_data[i]['next_match_index'] = match_index_map[next_match_key]
            else:
                logging.warning(f"Could not find next match index for R{current_round} M{current_match_num} -> R{next_round} M{next_match_num}")

    # Auto-advance winners from Round 1 byes
    # This needs to happen *after* next_match_index is set
    for i, match in enumerate(matches_data):
        if match['round_number'] == 1 and match['status'] == 'completed' and match['winner_id'] is not None:
            winner_id = match['winner_id']
            next_idx = match.get('next_match_index')

            if next_idx is not None and 0 <= next_idx < len(matches_data):
                next_match = matches_data[next_idx]
                # Determine if winner goes to player1 or player2 slot based on current match number
                if match['match_number'] % 2 != 0: # Odd match number -> player1 slot
                    if next_match['player1_id'] is None: # Avoid overwriting
                        next_match['player1_id'] = winner_id
                else: # Even match number -> player2 slot
                    if next_match['player2_id'] is None:
                        next_match['player2_id'] = winner_id

                # Update next match status if both players are now present
                if next_match['player1_id'] is not None and next_match['player2_id'] is not None:
                    next_match['status'] = 'pending' # Ready to play
            elif next_idx is not None:
                 logging.warning(f"Invalid next_match_index {next_idx} calculated for match {i}")

    logging.info(f"Generated and linked {len(matches_data)} match structures for tournament {tournament_id}")
    return matches_data


# Removed update_match_result function - logic moved to routes.py transaction
# Removed propagate_auto_advance helper function

def update_match_result(match_id: str, winner_id: str) -> bool:
    """
    Update match result and handle advancement logic.
    This is a wrapper function that delegates to routes.py implementation.
    
    Args:
        match_id (str): The ID of the match to update.
        winner_id (str): The ID of the winning player.
        
    Returns:
        bool: True if update was successful, False otherwise.
    """
    logging.warning("update_match_result called from tournament.py - this is a stub function")
    # This is just a stub to satisfy imports
    # The actual implementation is in routes.py
    return True

def get_tournament_bracket(tournament_id: str) -> dict:
    """
    Fetch matches and players from Firestore and structure data for the bracket view.

    Args:
        tournament_id (str): The ID of the tournament.

    Returns:
        dict: Data structure containing rounds of matches and player info, e.g.,
              {
                  'rounds': { 
                      1: [ {match_data_with_player_names...}, ... ],
                      2: [ ... ]
                  },
                  'players': {
                      'player_id1': {'name': '...', 'school': '...'},
                      ...
                  },
                  'error': None or 'Error message'
              }
    """
    if not db_firestore:
        logging.error("Firestore client not available in get_tournament_bracket")
        return {'rounds': {}, 'players': {}, 'error': 'Database connection not available. Please try again later.'}

    bracket_data = {'rounds': {}, 'players': {}, 'error': None}
    try:
        # 1. Validate tournament exists
        tournament_ref = db_firestore.collection('tournaments').document(tournament_id)
        tournament_doc = tournament_ref.get()
        
        if not tournament_doc.exists:
            logging.error(f"Tournament {tournament_id} does not exist")
            return {'rounds': {}, 'players': {}, 'error': 'Tournament not found. It may have been deleted.'}
            
        # 2. Get all players for the tournament
        players_ref = db_firestore.collection('players').where('tournament_id', '==', tournament_id)
        player_docs = players_ref.stream()
        players_dict = {}
        for doc in player_docs:
            player_data = doc.to_dict()
            # Include only necessary info for bracket display
            players_dict[doc.id] = {
                 'name': player_data.get('name', 'Unknown'),
                 'school': player_data.get('school', '')
            }
        bracket_data['players'] = players_dict
        logging.debug(f"Fetched {len(players_dict)} players for bracket {tournament_id}")
        
        if not players_dict:
            logging.info(f"No players found for tournament {tournament_id}")
            # Return empty data without error - frontend will handle as "no players" message
            return bracket_data

        # 3. Get all matches for the tournament, ordered by round and match number
        matches_ref = db_firestore.collection('matches')\
                                .where('tournament_id', '==', tournament_id)\
                                .order_by('round_number')\
                                .order_by('match_number')
        
        # Convert to list for easier counting and iteration
        match_docs_list = list(matches_ref.stream())
        logging.debug(f"Firestore query for matches returned {len(match_docs_list)} documents for tournament {tournament_id}")
        
        if not match_docs_list:
            logging.info(f"No matches found for tournament {tournament_id}")
            # Return empty data without error - frontend will handle as "need to generate bracket" message
            return bracket_data

        # Organize matches by round
        rounds = defaultdict(list)
        processed_count = 0
        
        for doc in match_docs_list:
            try:
                match_data = doc.to_dict()
                match_data['id'] = doc.id # Add Firestore document ID
                
                # Add player names
                p1_id = match_data.get('player1_id')
                p2_id = match_data.get('player2_id')
                w_id = match_data.get('winner_id')

                match_data['player1_name'] = players_dict.get(p1_id, {}).get('name') if p1_id else None
                match_data['player2_name'] = players_dict.get(p2_id, {}).get('name') if p2_id else None
                match_data['winner_name'] = players_dict.get(w_id, {}).get('name') if w_id else None
                
                # Add player school information
                match_data['player1_school'] = players_dict.get(p1_id, {}).get('school') if p1_id else None
                match_data['player2_school'] = players_dict.get(p2_id, {}).get('school') if p2_id else None

                round_num = match_data.get('round_number')
                if round_num is not None:
                    rounds[round_num].append(match_data)
                    processed_count += 1
                else:
                    logging.warning(f"Match {doc.id} missing or has null round_number for tournament {tournament_id}. Skipping.")
            except Exception as process_error:
                logging.error(f"Error processing match document {doc.id}: {process_error}", exc_info=True)
                # Continue processing other matches

        bracket_data['rounds'] = dict(rounds) # Convert defaultdict to dict
        
        logging.debug(f"Finished processing. Added matches to {len(rounds)} rounds. Total matches processed: {processed_count} for bracket {tournament_id}")

    except Exception as e:
        logging.error(f"Error fetching bracket data for tournament {tournament_id}: {e}", exc_info=True)
        bracket_data['error'] = f"Error retrieving bracket data: {str(e)[:100]}... (Please contact administrator)"

    return bracket_data
