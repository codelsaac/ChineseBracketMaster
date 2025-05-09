# Application routes and views
import logging
from flask import render_template, request, redirect, url_for, jsonify, flash, abort
from datetime import datetime
import json
from google.cloud.firestore import Client, Transaction, DocumentReference, DocumentSnapshot, Query
from google.cloud import firestore # <-- Add this import
from google.api_core.exceptions import NotFound

# Import the Firestore client from app.py
from app import app, db_firestore
# Removed SQLAlchemy model imports
# from models import Player, Tournament, Match

# Import functions from tournament.py (these might need adjustments later)
# Assuming these functions will be adapted to work with Firestore data structures
from tournament import create_tournament_bracket, update_match_result, get_tournament_bracket

# --- Helper Functions for Firestore ---

def _get_doc_or_404(doc_ref: DocumentReference) -> DocumentSnapshot:
    """Gets a Firestore document or raises 404."""
    try:
        doc = doc_ref.get()
        if not doc.exists:
            abort(404, description=f"Document not found: {doc_ref.path}")
        return doc
    except NotFound:
        abort(404, description=f"Document not found: {doc_ref.path}")
    except Exception as e:
        logging.error(f"Error fetching document {doc_ref.path}: {e}")
        abort(500, description="Error accessing database")

def _doc_to_dict(doc: DocumentSnapshot) -> dict:
    """Converts a Firestore document snapshot to a dict, adding the ID."""
    data = doc.to_dict()
    if data is not None:
        data['id'] = doc.id
    return data

# --- Routes ---

@app.route('/')
def index():
    """Home page with list of tournaments"""
    if not db_firestore:
        flash("Database connection not available.", "error")
        return render_template('index.html', tournaments=[])
    try:
        tournaments_ref = db_firestore.collection('tournaments').order_by('date', direction=Query.DESCENDING)
        docs = tournaments_ref.stream()
        tournaments = [_doc_to_dict(doc) for doc in docs]
        # Convert Firestore Timestamp to Date string for template if needed
        for t in tournaments:
            if 'date' in t and isinstance(t['date'], datetime):
                t['date_str'] = t['date'].strftime('%Y-%m-%d') # Or keep as datetime object if template handles it
    except Exception as e:
        logging.error(f"Error fetching tournaments: {e}")
        flash("Error fetching tournaments.", "error")
        tournaments = []
    return render_template('index.html', tournaments=tournaments)

@app.route('/tournament/new', methods=['POST'])
def new_tournament():
    """Create a new tournament"""
    if not db_firestore:
        flash("Database connection not available.", "error")
        return redirect(url_for('index'))
    try:
        name = request.form.get('name')
        date_str = request.form.get('date')
        
        if not name or not date_str:
            flash('Tournament name and date are required', 'error')
            return redirect(url_for('index'))
        
        # Convert date string to Firestore Timestamp (more flexible than Date)
        try:
            tournament_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('index'))
        
        tournament_data = {
            'name': name,
            'date': tournament_date, # Store as Firestore Timestamp
            'status': 'setup' # setup, in_progress, completed
        }
        # Add new tournament document, Firestore auto-generates ID
        update_time, doc_ref = db_firestore.collection('tournaments').add(tournament_data)
        
        flash(f'Tournament "{name}" created successfully', 'success')
        # Redirect to player management for the new tournament ID (string)
        return redirect(url_for('players', tournament_id=doc_ref.id))
    except Exception as e:
        logging.error(f"Error creating tournament: {e}")
        flash(f'Error creating tournament: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/tournament/<string:tournament_id>/players')
def players(tournament_id):
    """Page for managing players in a tournament"""
    if not db_firestore:
        flash("Database connection not available.", "error")
        return redirect(url_for('index'))

    tournament_ref = db_firestore.collection('tournaments').document(tournament_id)
    tournament_doc = _get_doc_or_404(tournament_ref)
    tournament = _doc_to_dict(tournament_doc)

    players_list = []
    try:
        players_query = db_firestore.collection('players').where('tournament_id', '==', tournament_id).order_by('name')
        docs = players_query.stream()
        players_list = [_doc_to_dict(doc) for doc in docs]
    except Exception as e:
        logging.error(f"Error fetching players for tournament {tournament_id}: {e}")
        flash("Error fetching players.", "error")

    return render_template('players.html', tournament=tournament, players=players_list)

@app.route('/tournament/<string:tournament_id>/add_player', methods=['POST'])
def add_player(tournament_id):
    """Add a player to a tournament"""
    if not db_firestore:
        flash("Database connection not available.", "error")
        return redirect(url_for('players', tournament_id=tournament_id))

    tournament_ref = db_firestore.collection('tournaments').document(tournament_id)
    _get_doc_or_404(tournament_ref) # Ensure tournament exists

    try:
        name = request.form.get('name')
        school = request.form.get('school')
        is_seeded = request.form.get('is_seeded') == 'on'
        
        if not name or not school:
            flash('Player name and school are required', 'error')
            return redirect(url_for('players', tournament_id=tournament_id))
        
        # Check if a player with the same name and school already exists in this tournament
        players_ref = db_firestore.collection('players')
        existing_player_query = players_ref.where('tournament_id', '==', tournament_id).where('name', '==', name).where('school', '==', school).limit(1)
        existing_docs = list(existing_player_query.stream()) # Use list() to execute query
        
        if existing_docs:
            flash(f'A player named "{name}" from "{school}" already exists in this tournament', 'error')
            return redirect(url_for('players', tournament_id=tournament_id))
        
        player_data = {
            'name': name,
            'school': school,
            'is_seeded': is_seeded,
            'tournament_id': tournament_id # Store tournament ID as string
            # Consider adding an 'order' field if drag-and-drop requires it
        }
        db_firestore.collection('players').add(player_data)
        
        flash(f'Player "{name}" added successfully', 'success')
    except Exception as e:
        logging.error(f"Error adding player to tournament {tournament_id}: {e}")
        flash(f'Error adding player: {str(e)}', 'error')
    
    return redirect(url_for('players', tournament_id=tournament_id))

@app.route('/tournament/<string:tournament_id>/edit_player/<string:player_id>', methods=['POST'])
def edit_player(tournament_id, player_id):
    """Edit a player's details"""
    if not db_firestore:
        flash("Database connection not available.", "error")
        return redirect(url_for('players', tournament_id=tournament_id))

    player_ref = db_firestore.collection('players').document(player_id)
    player_doc = _get_doc_or_404(player_ref)
    player_data = _doc_to_dict(player_doc)

    # Ensure player belongs to the specified tournament
    if player_data.get('tournament_id') != tournament_id:
        flash('Player does not belong to this tournament', 'error')
        return redirect(url_for('players', tournament_id=tournament_id))

    try:
        new_name = request.form.get('name')
        new_school = request.form.get('school')
        new_is_seeded = request.form.get('is_seeded') == 'on'
        
        if not new_name or not new_school:
             flash('Player name and school cannot be empty.', 'error')
             return redirect(url_for('players', tournament_id=tournament_id))

        # Check for duplicates, excluding the current player
        players_ref = db_firestore.collection('players')
        existing_player_query = players_ref.where('tournament_id', '==', tournament_id) \
                                         .where('name', '==', new_name) \
                                         .where('school', '==', new_school)

        existing_docs = list(existing_player_query.stream())

        # Filter out the current player from the results
        duplicate_exists = False
        for doc in existing_docs:
            if doc.id != player_id:
                duplicate_exists = True
                break

        if duplicate_exists:
            flash(f'Another player named "{new_name}" from "{new_school}" already exists in this tournament', 'error')
            return redirect(url_for('players', tournament_id=tournament_id))

        # Update player data
        update_data = {
            'name': new_name,
            'school': new_school,
            'is_seeded': new_is_seeded
        }
        player_ref.update(update_data)

        flash('Player updated successfully', 'success')
    except Exception as e:
        logging.error(f"Error updating player {player_id}: {e}")
        flash(f'Error updating player: {str(e)}', 'error')

    return redirect(url_for('players', tournament_id=tournament_id))

@app.route('/tournament/<string:tournament_id>/delete_player/<string:player_id>', methods=['POST'])
def delete_player(tournament_id, player_id):
    """Delete a player from a tournament. Needs careful handling if bracket exists."""
    if not db_firestore:
        flash("Database connection not available.", "error")
        return redirect(url_for('players', tournament_id=tournament_id))

    player_ref = db_firestore.collection('players').document(player_id)
    player_doc = _get_doc_or_404(player_ref)
    player_data = _doc_to_dict(player_doc)

    tournament_ref = db_firestore.collection('tournaments').document(tournament_id)
    tournament_doc = _get_doc_or_404(tournament_ref)
    tournament_data = _doc_to_dict(tournament_doc)

    # Ensure player belongs to the specified tournament
    if player_data.get('tournament_id') != tournament_id:
        flash('Player does not belong to this tournament', 'error')
        return redirect(url_for('players', tournament_id=tournament_id))

    try:
        # If tournament has started, deleting players can corrupt the bracket.
        # Option 1: Prevent deletion if tournament is in progress/completed.
        # Option 2: Allow deletion but clear the player from matches (complex).
        # Implementing Option 1 for simplicity.
        if tournament_data.get('status') in ['in_progress', 'completed']:
            flash('Cannot delete players after the tournament bracket has been generated.', 'error')
            return redirect(url_for('players', tournament_id=tournament_id))

        # Delete the player document
        player_ref.delete()
        flash('Player deleted successfully', 'success')

    except Exception as e:
        logging.error(f"Error deleting player {player_id}: {e}")
        flash(f'Error deleting player: {str(e)}', 'error')

    return redirect(url_for('players', tournament_id=tournament_id))

@app.route('/tournament/<string:tournament_id>/generate_bracket', methods=['POST'])
def generate_bracket(tournament_id):
    """Generate the tournament bracket using Firestore data."""
    if not db_firestore:
        flash("Database connection not available.", "error")
        return redirect(url_for('players', tournament_id=tournament_id))

    tournament_ref = db_firestore.collection('tournaments').document(tournament_id)
    tournament_doc = _get_doc_or_404(tournament_ref)
    # tournament_data = _doc_to_dict(tournament_doc) # Raw data if needed

    try:
        # Fetch players for the tournament from Firestore
        players_query = db_firestore.collection('players').where('tournament_id', '==', tournament_id)
        player_docs = list(players_query.stream()) # Execute query

        if len(player_docs) < 2:
            flash('At least 2 players are required to generate a bracket', 'error')
            return redirect(url_for('players', tournament_id=tournament_id))

        players_list = [_doc_to_dict(doc) for doc in player_docs]

        # --- Clear existing matches for this tournament ---
        # This is crucial to prevent duplicate/old matches.
        # Use a batch delete for efficiency.
        existing_matches_query = db_firestore.collection('matches').where('tournament_id', '==', tournament_id)
        existing_match_docs = list(existing_matches_query.stream()) # Get all docs to delete
        if existing_match_docs:
            batch = db_firestore.batch()
            for doc in existing_match_docs:
                batch.delete(doc.reference)
            batch.commit()
            logging.info(f"Deleted {len(existing_match_docs)} existing matches for tournament {tournament_id}")
        # --- End Clearing ---

        # Prepare player data structure expected by create_tournament_bracket
        # Assuming it needs a list of dictionaries with 'id', 'name', 'school', 'is_seeded'
        # Adapt this based on the actual requirements of create_tournament_bracket
        players_for_bracket = players_list # Use the list fetched earlier

        # Generate new bracket structure (list of match dictionaries)
        # IMPORTANT: create_tournament_bracket needs to be adapted for Firestore IDs (strings)
        # and return data compatible with Firestore (e.g., player IDs as strings)
        try:
             # Pass string IDs
            generated_matches_data = create_tournament_bracket(tournament_id, players_for_bracket)
        except Exception as bracket_error:
             logging.error(f"Error calling create_tournament_bracket for {tournament_id}: {bracket_error}")
             flash(f"Internal error during bracket generation: {bracket_error}", "error")
             return redirect(url_for('players', tournament_id=tournament_id))


        # Save generated matches and link them using Firestore IDs
        if generated_matches_data:
            matches_ref = db_firestore.collection('matches')
            match_refs_with_indices = [] # Store tuples of (doc_ref, original_index)
            batch_create = db_firestore.batch()

            # First pass: Create all match documents and store their refs + original index
            for i, match_data in enumerate(generated_matches_data):
                match_data['tournament_id'] = tournament_id
                # Don't save next_match_index to Firestore
                next_match_idx = match_data.pop('next_match_index', None)
                new_match_ref = matches_ref.document() # Generate ref for new doc
                batch_create.set(new_match_ref, match_data)
                # Corrected variable name here
                match_refs_with_indices.append({'ref': new_match_ref, 'original_index': i, 'next_match_original_index': next_match_idx})

            batch_create.commit()
            logging.info(f"Created {len(generated_matches_data)} match documents for tournament {tournament_id}")

            # Create a map from original index to Firestore document ID
            index_to_id_map = {item['original_index']: item['ref'].id for item in match_refs_with_indices}

            # Second pass: Update matches with the correct next_match_id
            batch_update = db_firestore.batch()
            updates_prepared = 0
            for item in match_refs_with_indices:
                next_original_idx = item.get('next_match_original_index')
                if next_original_idx is not None:
                    next_match_firestore_id = index_to_id_map.get(next_original_idx)
                    if next_match_firestore_id:
                        batch_update.update(item['ref'], {'next_match_id': next_match_firestore_id})
                        updates_prepared += 1
                    else:
                        logging.warning(f"Could not find Firestore ID for next_match_index {next_original_idx} when updating match {item['ref'].id}")

            if updates_prepared > 0:
                batch_update.commit()
                logging.info(f"Updated {updates_prepared} matches with next_match_id links for tournament {tournament_id}")

        else:
            logging.warning(f"create_tournament_bracket returned no matches for {tournament_id}")


        # Update tournament status
        tournament_ref.update({'status': 'in_progress'})

        flash('Tournament bracket generated successfully', 'success')
        return redirect(url_for('view_tournament', tournament_id=tournament_id))

    except Exception as e:
        logging.error(f"Error generating bracket for tournament {tournament_id}: {e}")
        # Rollback not needed explicitly for Firestore batch/single ops unless using transactions
        flash(f'Error generating bracket: {str(e)}', 'error')
        # Attempt to reset status if generation failed mid-way? Maybe not necessary.
        # tournament_ref.update({'status': 'setup'})
        return redirect(url_for('players', tournament_id=tournament_id))


@app.route('/tournament/<string:tournament_id>')
def view_tournament(tournament_id):
    """View tournament bracket page"""
    if not db_firestore:
        flash("Database connection not available.", "error")
        # Decide how to render - maybe a minimal page indicating DB error
        return render_template('tournament.html', tournament={'id': tournament_id, 'name': 'Error Loading Tournament', 'error': True}, bracket_data=None)

    tournament_ref = db_firestore.collection('tournaments').document(tournament_id)
    tournament_doc = _get_doc_or_404(tournament_ref)
    tournament = _doc_to_dict(tournament_doc)
    if 'date' in tournament and isinstance(tournament['date'], datetime):
         tournament['date_str'] = tournament['date'].strftime('%Y-%m-%d')


    # The actual bracket data is fetched via API, so just pass the tournament info
    return render_template('tournament.html', tournament=tournament) # Pass tournament dict


@app.route('/api/tournament/<string:tournament_id>/bracket')
def get_bracket(tournament_id):
    """API endpoint to get tournament bracket data from Firestore."""
    if not db_firestore:
        return jsonify({'error': 'Database connection not available.'}), 503

    try:
        # IMPORTANT: get_tournament_bracket function needs modification
        # to fetch data from Firestore instead of SQLAlchemy.
        # It should query the 'matches' collection for the given tournament_id
        # and potentially the 'players' collection to populate player names.
        bracket_data = get_tournament_bracket(tournament_id) # Pass string ID
        return jsonify(bracket_data)
    except Exception as e:
        logging.error(f"API Error fetching bracket for {tournament_id}: {e}")
        return jsonify({'error': f'Failed to retrieve bracket data: {str(e)}'}), 500

# IMPORTANT: Changed match_id to string
@app.route('/api/match/<string:match_id>/update', methods=['POST'])
def update_match(match_id):
    """API endpoint to update match result in Firestore."""
    logging.info(f"Received request to update match {match_id}") # <-- Add initial log
    try:
        data = request.get_json()
        logging.info(f"Request payload for match {match_id}: {data}") # <-- Log payload
    except Exception as e:
        logging.error(f"Error getting JSON payload for match {match_id}: {e}")
        return jsonify({'success': False, 'error': 'Invalid request format.'}), 400
        
    if not db_firestore:
        logging.error(f"Database connection error during update for match {match_id}")
        return jsonify({'success': False, 'error': 'Database connection not available.'}), 503

    # Rest of the function remains the same...
    try:
        # data = request.get_json() # Moved payload retrieval up
        if not data:
            # This check might be redundant now but kept for safety
            logging.warning(f"Empty payload received for match {match_id}")
            return jsonify({'success': False, 'error': 'Invalid request body.'}), 400
        
        winner_id = data.get('winner_id') # Expecting string player ID or null/None

        # Basic validation for winner_id format if not None
        if winner_id is not None and not isinstance(winner_id, str):
             logging.warning(f"Invalid winner_id format received for match {match_id}: {winner_id}")
             return jsonify({'success': False, 'error': 'Invalid winner_id format.'}), 400

        match_ref = db_firestore.collection('matches').document(match_id)

        # Use a transaction to ensure atomic update and advancement
        @firestore.transactional
        def update_in_transaction(transaction: Transaction, match_ref_tx: DocumentReference, winner_id_tx: str):
            logging.info(f"[Transaction {transaction.id}] Attempting to get match snapshot for {match_ref_tx.id}") # <-- Added log
            match_snapshot = match_ref_tx.get(transaction=transaction)
            if not match_snapshot.exists:
                logging.error(f"[Transaction {transaction.id}] Match {match_ref_tx.id} not found during transaction.") # <-- Added log
                # Raise specific exception to be caught outside
                raise NotFound(f"Match {match_ref_tx.id} not found")
            
            logging.info(f"[Transaction {transaction.id}] Successfully retrieved match snapshot for {match_ref_tx.id}") # <-- Added log
            match_data = match_snapshot.to_dict()
            tournament_id_tx = match_data.get('tournament_id')
            current_match_number = match_data.get('match_number')
            next_match_id = match_data.get('next_match_id')

            if not tournament_id_tx:
                 logging.error(f"[Transaction {transaction.id}] Match {match_ref_tx.id} is missing tournament_id") # <-- Added log
                 raise ValueError(f"Match {match_ref_tx.id} is missing tournament_id")
            if current_match_number is None:
                 logging.error(f"[Transaction {transaction.id}] Match {match_ref_tx.id} is missing match_number") # <-- Added log
                 raise ValueError(f"Match {match_ref_tx.id} is missing match_number")

            # Update the winner_id for the current match
            update_data = {
                'winner_id': winner_id_tx,
                'status': 'completed' if winner_id_tx else 'pending' # Update status
            }
            logging.info(f"[Transaction {transaction.id}] Attempting to update match {match_ref_tx.id} with: {update_data}") # <-- Added log
            # --- Prepare for Advancing Winner (Read Next Match First) ---
            next_match_ref = None
            next_match_snapshot = None
            if next_match_id and winner_id_tx:
                logging.info(f"[Transaction {transaction.id}] Preparing to advance winner. Next match ID: {next_match_id}")
                next_match_ref = db_firestore.collection('matches').document(next_match_id)
                logging.info(f"[Transaction {transaction.id}] Attempting to get next match snapshot for {next_match_id} (Read before write)")
                next_match_snapshot = next_match_ref.get(transaction=transaction) # Read next match BEFORE writing current match
                if next_match_snapshot.exists:
                    logging.info(f"[Transaction {transaction.id}] Successfully retrieved next match snapshot for {next_match_id}")
                else:
                    logging.warning(f"[Transaction {transaction.id}] Next match {next_match_id} does not exist.")

            # --- Update Current Match (Write Operation) ---
            transaction.update(match_ref_tx, update_data)
            logging.info(f"[Transaction {transaction.id}] Successfully updated current match {match_ref_tx.id}: winner={winner_id_tx}, status={'completed' if winner_id_tx else 'pending'}")

            # --- Update Next Match (Write Operation, if applicable) ---
            if next_match_ref and next_match_snapshot and next_match_snapshot.exists and winner_id_tx:
                next_match_data = next_match_snapshot.to_dict()
                update_payload = {}
                is_player1_slot = current_match_number % 2 != 0

                if is_player1_slot:
                    target_slot = 'player1_id'
                    other_slot = 'player2_id'
                else:
                    target_slot = 'player2_id'
                    other_slot = 'player1_id'

                # Check if the target slot is already filled correctly or needs update
                if next_match_data.get(target_slot) is None:
                    update_payload[target_slot] = winner_id_tx
                    logging.info(f"[Transaction {transaction.id}] Preparing to advance winner {winner_id_tx} to {target_slot} of next match {next_match_id}")
                elif next_match_data.get(target_slot) != winner_id_tx:
                    # Slot filled by someone else - log warning, don't overwrite
                    logging.warning(f"[Transaction {transaction.id}] Next match {next_match_id} {target_slot} already filled with {next_match_data.get(target_slot)}, cannot advance {winner_id_tx}")
                    # else: Slot already filled correctly, no update needed for this slot

                # Determine if the next match becomes 'pending' (This should happen regardless of the slot update)
                # Check current state + potential update
                player1_now_present = (target_slot == 'player1_id' and target_slot in update_payload) or (next_match_data.get('player1_id') is not None)
                player2_now_present = (target_slot == 'player2_id' and target_slot in update_payload) or (next_match_data.get('player2_id') is not None)

                if player1_now_present and player2_now_present and next_match_data.get('status') != 'completed':
                    update_payload['status'] = 'pending'
                    logging.info(f"[Transaction {transaction.id}] Setting next match {next_match_id} status to 'pending'")

                if update_payload: # Only update if there's something to change
                    logging.info(f"[Transaction {transaction.id}] Attempting to update next match {next_match_id} with payload: {update_payload}") # <-- Added log
                    transaction.update(next_match_ref, update_payload)
                    logging.info(f"[Transaction {transaction.id}] Successfully updated next match {next_match_id}") # <-- Added log
            # This else corresponds to the outer 'if next_match_ref and next_match_snapshot and next_match_snapshot.exists and winner_id_tx:'
            # It handles cases where the next match doesn't exist or wasn't retrieved.
            # The original logging.warning seemed misplaced under the inner else.
            # Let's refine the logging based on the outer condition.
            elif not (next_match_ref and next_match_snapshot and next_match_snapshot.exists and winner_id_tx):
                 if next_match_id and winner_id_tx:
                     logging.warning(f"[Transaction {transaction.id}] Next match {next_match_id} referenced by match {match_ref_tx.id} not found or snapshot retrieval failed during transaction.")
                 # Other cases handled below
            elif next_match_id and not winner_id_tx:
                 logging.info(f"[Transaction {transaction.id}] No winner for match {match_ref_tx.id}, not advancing to {next_match_id}.") # <-- Added log
            elif not next_match_id:
                 logging.info(f"[Transaction {transaction.id}] Match {match_ref_tx.id} has no next_match_id.") # <-- Added log
            
            # Check if this was the final match and update tournament status
            is_final = not next_match_id
            if is_final and winner_id_tx:
                logging.info(f"[Transaction {transaction.id}] Final match {match_ref_tx.id} completed. Attempting to update tournament {tournament_id_tx} status.") # <-- Added log
                tournament_ref_tx = db_firestore.collection('tournaments').document(tournament_id_tx)
                transaction.update(tournament_ref_tx, {'status': 'completed'})
                logging.info(f"[Transaction {transaction.id}] Successfully updated tournament {tournament_id_tx} status to 'completed'.")
            elif is_final and not winner_id_tx:
                 logging.info(f"[Transaction {transaction.id}] Final match {match_ref_tx.id} winner cleared, not updating tournament status.") # <-- Added log

        # Execute the transaction
        logging.info(f"Attempting transaction for match {match_id} with winner {winner_id}")
        transaction_result = update_in_transaction(db_firestore.transaction(), match_ref, winner_id)
        logging.info(f"Transaction for match {match_id} completed successfully.") # <-- Added log
        
        # If transaction successful
        logging.info(f"Successfully updated match {match_id}")
        return jsonify({'success': True})

    except NotFound as e:
        logging.error(f"Error updating match {match_id} (NotFound): {e}") # <-- Added log
        return jsonify({'success': False, 'error': str(e)}), 404
    except ValueError as e:
        logging.error(f"Error updating match {match_id} (ValueError): {e}") # <-- Added log
        return jsonify({'success': False, 'error': str(e)}), 400 # Bad request due to data inconsistency
    except Exception as e:
        # Catch any other unexpected errors during the process
        logging.exception(f"Unexpected error updating match {match_id}: {e}") # Use logging.exception to include traceback
        return jsonify({'success': False, 'error': 'An internal server error occurred.'}), 500


@app.route('/tournament/<string:tournament_id>/export/pdf')
def export_bracket_pdf(tournament_id):
    """Export the tournament bracket as a PDF (Placeholder)."""
    # This requires a PDF generation library (e.g., ReportLab, WeasyPrint)
    # Fetch bracket data, format it, generate PDF
    flash('PDF export functionality is not yet implemented.', 'info')
    return redirect(url_for('view_tournament', tournament_id=tournament_id))

# --- Error Handlers ---
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', error=e), 404

@app.errorhandler(500)
def internal_server_error(e):
    # Log the error
    logging.exception('An internal server error occurred.') 
    # note that we set the 500 status explicitly
    return render_template('500.html', error=e), 500

# Add any other routes from the original file if they were missed
# Ensure all <int:id> are changed to <string:id> where appropriate

# Example: Route for updating player order via drag/drop
@app.route('/api/tournament/<string:tournament_id>/update_player_order', methods=['POST'])
def update_player_order(tournament_id):
    if not db_firestore:
        return jsonify({'error': 'Database connection not available.'}), 503
    try:
        data = request.get_json()
        ordered_player_ids = data.get('player_ids') # Expecting a list of player IDs (strings) in desired order

        if not isinstance(ordered_player_ids, list):
            return jsonify({'error': 'Invalid data format. Expected player_ids list.'}), 400

        # Use a batch write to update an 'order' field for each player
        batch = db_firestore.batch()
        players_ref = db_firestore.collection('players')
        for index, player_id in enumerate(ordered_player_ids):
            # Added check for non-string IDs before creating document reference
            if not isinstance(player_id, str):
                logging.warning(f"Skipping non-string player ID in order update: {player_id}")
                continue # Skip non-string IDs
            player_ref = players_ref.document(player_id)
            # Check if player actually belongs to this tournament? Maybe not needed if UI prevents it.
            batch.update(player_ref, {'ui_order': index}) # Add/Update an order field

        batch.commit()
        return jsonify({'status': 'success', 'message': 'Player order updated.'})
    except Exception as e:
        logging.error(f"Error updating player order for tournament {tournament_id}: {e}")
        return jsonify({'error': f'Failed to update player order: {str(e)}'}), 500

# Add any other routes from the original file if they were missed
# Ensure all <int:id> are changed to <string:id> where appropriate

@app.route('/tournament/<string:tournament_id>/delete', methods=['POST'])
def delete_tournament(tournament_id):
    app.logger.info(f'Received request to delete tournament with ID: {tournament_id}') # Add app logger
    """Delete a tournament and all its related data."""
    if not db_firestore:
        flash("Database connection not available.", "error")
        return redirect(url_for('index'))

    tournament_ref = db_firestore.collection('tournaments').document(tournament_id)
    tournament_doc = _get_doc_or_404(tournament_ref)
    tournament_data = _doc_to_dict(tournament_doc)
    logging.info(f"Attempting to delete tournament: {tournament_id} - {tournament_data.get('name')}")

    try:
        # 使用批處理刪除所有相關數據
        batch = db_firestore.batch()
        logging.debug(f"Starting batch delete for tournament {tournament_id}")

        # 1. 刪除所有相關的比賽
        matches_query = db_firestore.collection('matches').where('tournament_id', '==', tournament_id)
        matches_docs = list(matches_query.stream())
        logging.info(f"Found {len(matches_docs)} matches to delete for tournament {tournament_id}")
        for doc in matches_docs:
            logging.debug(f"Adding match {doc.id} to delete batch")
            batch.delete(doc.reference)
        
        # 2. 刪除所有相關的選手
        players_query = db_firestore.collection('players').where('tournament_id', '==', tournament_id)
        players_docs = list(players_query.stream())
        logging.info(f"Found {len(players_docs)} players to delete for tournament {tournament_id}")
        for doc in players_docs:
            logging.debug(f"Adding player {doc.id} to delete batch")
            batch.delete(doc.reference)
        
        # 3. 最後刪除比賽本身
        batch.delete(tournament_ref)
        
        # 3. 最後刪除比賽本身
        logging.debug(f"Adding tournament {tournament_id} itself to delete batch")
        batch.delete(tournament_ref)

        # 提交批處理操作
        logging.info(f"Committing batch delete for tournament {tournament_id}")
        batch.commit()
        logging.info(f"Batch delete committed successfully for tournament {tournament_id}")
        
        flash(f'比賽 "{tournament_data.get("name")}" 已成功刪除', 'success')
    except Exception as e:
        logging.error(f"Error deleting tournament {tournament_id}: {e}")
        flash(f'刪除比賽時發生錯誤: {str(e)}', 'error')
    
    return redirect(url_for('index'))
