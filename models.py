# SQLAlchemy models have been removed as part of the migration to Firebase Firestore.
# You will need to redefine your data structures and access logic
# using the Firebase Admin SDK (db_firestore client) in your routes.

# Example Firestore Structure (adjust as needed):

# /tournaments/{tournament_id}
#   - name: "Tournament Name"
#   - date: ...
#   - status: "active" / "completed"

# /players/{player_id}
#   - name: "Player Name"
#   - school: "School Name"
#   - is_seed: True/False
#   - tournament_ref: /tournaments/{tournament_id}  (or store tournament_id directly)

# /matches/{match_id}
#   - tournament_ref: /tournaments/{tournament_id}
#   - round: 1
#   - player1_ref: /players/{player_id} (or None for bye)
#   - player2_ref: /players/{player_id} (or None for bye)
#   - winner_ref: /players/{player_id} (or None if not played)
#   - status: "pending" / "completed"

# Access Firestore using the 'db_firestore' client initialized in app.py
# from app import db_firestore
