# Chinese Chess Competition Management System
# Entry point for the application
from app import app
print("DEBUG: Before importing routes") # Add this
import routes  # noqa: F401
print("DEBUG: After importing routes") # Add this

if __name__ == "__main__":
    print("DEBUG: Inside __main__ block") # Add this
    app.logger.info("Starting Flask development server...")
    app.run(host="0.0.0.0", port=5000, debug=True)
