# Application routes and views
from flask import render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime
import json

from app import app, db
from models import Player, Tournament, Match
from tournament import create_tournament_bracket, update_match_result, get_tournament_bracket

@app.route('/')
def index():
    """Home page with list of tournaments"""
    tournaments = Tournament.query.all()
    return render_template('index.html', tournaments=tournaments)

@app.route('/tournament/new', methods=['POST'])
def new_tournament():
    """Create a new tournament"""
    try:
        name = request.form.get('name')
        date_str = request.form.get('date')
        
        if not name or not date_str:
            flash('Tournament name and date are required', 'error')
            return redirect(url_for('index'))
        
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        tournament = Tournament(name=name, date=date, status='setup')
        db.session.add(tournament)
        db.session.commit()
        
        flash(f'Tournament "{name}" created successfully', 'success')
        return redirect(url_for('players', tournament_id=tournament.id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating tournament: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/tournament/<int:tournament_id>/players')
def players(tournament_id):
    """Page for managing players in a tournament"""
    tournament = Tournament.query.get_or_404(tournament_id)
    players = Player.query.filter_by(tournament_id=tournament_id).all()
    return render_template('players.html', tournament=tournament, players=players)

@app.route('/tournament/<int:tournament_id>/add_player', methods=['POST'])
def add_player(tournament_id):
    """Add a player to a tournament"""
    try:
        tournament = Tournament.query.get_or_404(tournament_id)
        
        name = request.form.get('name')
        school = request.form.get('school')
        is_seeded = request.form.get('is_seeded') == 'on'
        
        if not name or not school:
            flash('Player name and school are required', 'error')
            return redirect(url_for('players', tournament_id=tournament_id))
        
        player = Player(
            name=name,
            school=school,
            is_seeded=is_seeded,
            tournament_id=tournament_id
        )
        
        db.session.add(player)
        db.session.commit()
        
        flash(f'Player "{name}" added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding player: {str(e)}', 'error')
    
    return redirect(url_for('players', tournament_id=tournament_id))

@app.route('/tournament/<int:tournament_id>/edit_player/<int:player_id>', methods=['POST'])
def edit_player(tournament_id, player_id):
    """Edit a player's details"""
    try:
        player = Player.query.get_or_404(player_id)
        
        # Ensure player belongs to the specified tournament
        if player.tournament_id != tournament_id:
            flash('Player does not belong to this tournament', 'error')
            return redirect(url_for('players', tournament_id=tournament_id))
        
        player.name = request.form.get('name')
        player.school = request.form.get('school')
        player.is_seeded = request.form.get('is_seeded') == 'on'
        
        db.session.commit()
        flash('Player updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating player: {str(e)}', 'error')
    
    return redirect(url_for('players', tournament_id=tournament_id))

@app.route('/tournament/<int:tournament_id>/delete_player/<int:player_id>', methods=['POST'])
def delete_player(tournament_id, player_id):
    """Delete a player from a tournament"""
    try:
        player = Player.query.get_or_404(player_id)
        
        # Ensure player belongs to the specified tournament
        if player.tournament_id != tournament_id:
            flash('Player does not belong to this tournament', 'error')
            return redirect(url_for('players', tournament_id=tournament_id))
        
        db.session.delete(player)
        db.session.commit()
        flash('Player deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting player: {str(e)}', 'error')
    
    return redirect(url_for('players', tournament_id=tournament_id))

@app.route('/tournament/<int:tournament_id>/generate_bracket', methods=['POST'])
def generate_bracket(tournament_id):
    """Generate the tournament bracket"""
    try:
        tournament = Tournament.query.get_or_404(tournament_id)
        
        # Check if there are enough players
        player_count = Player.query.filter_by(tournament_id=tournament_id).count()
        if player_count < 2:
            flash('At least 2 players are required to generate a bracket', 'error')
            return redirect(url_for('players', tournament_id=tournament_id))
        
        # Delete existing matches if any
        Match.query.filter_by(tournament_id=tournament_id).delete()
        
        # Generate new bracket
        matches = create_tournament_bracket(tournament_id)
        
        # Save matches to database
        for match in matches:
            db.session.add(match)
        
        # Update tournament status
        tournament.status = 'in_progress'
        db.session.commit()
        
        flash('Tournament bracket generated successfully', 'success')
        return redirect(url_for('view_tournament', tournament_id=tournament_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error generating bracket: {str(e)}', 'error')
        return redirect(url_for('players', tournament_id=tournament_id))

@app.route('/tournament/<int:tournament_id>')
def view_tournament(tournament_id):
    """View tournament bracket"""
    tournament = Tournament.query.get_or_404(tournament_id)
    return render_template('tournament.html', tournament=tournament)

@app.route('/api/tournament/<int:tournament_id>/bracket')
def get_bracket(tournament_id):
    """API endpoint to get tournament bracket data"""
    try:
        bracket_data = get_tournament_bracket(tournament_id)
        return jsonify(bracket_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/match/<int:match_id>/update', methods=['POST'])
def update_match(match_id):
    """API endpoint to update match result"""
    try:
        data = request.get_json()
        winner_id = data.get('winner_id')
        
        if not winner_id:
            return jsonify({'error': 'Winner ID is required'}), 400
        
        success = update_match_result(match_id, winner_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to update match'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Custom 500 page"""
    return render_template('500.html'), 500
