# Database models for the application
from app import db

class Player(db.Model):
    """Model for players participating in tournaments"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(100), nullable=False)
    is_seeded = db.Column(db.Boolean, default=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    
    def to_dict(self):
        """Convert player model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'school': self.school,
            'is_seeded': self.is_seeded,
            'tournament_id': self.tournament_id
        }

class Tournament(db.Model):
    """Model for tournaments"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="setup")  # setup, in_progress, completed
    players = db.relationship('Player', backref='tournament', lazy=True)
    
    def to_dict(self):
        """Convert tournament model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date.isoformat(),
            'status': self.status,
            'players': [player.to_dict() for player in self.players]
        }

class Match(db.Model):
    """Model for tournament matches"""
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    match_number = db.Column(db.Integer, nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    player2_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    next_match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    
    # Define relationships
    tournament = db.relationship('Tournament', backref='matches')
    player1 = db.relationship('Player', foreign_keys=[player1_id])
    player2 = db.relationship('Player', foreign_keys=[player2_id])
    winner = db.relationship('Player', foreign_keys=[winner_id])
    next_match = db.relationship('Match', remote_side=[id], backref='previous_matches')
    
    def to_dict(self):
        """Convert match model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'round_number': self.round_number,
            'match_number': self.match_number,
            'player1_id': self.player1_id,
            'player2_id': self.player2_id,
            'winner_id': self.winner_id,
            'next_match_id': self.next_match_id
        }
