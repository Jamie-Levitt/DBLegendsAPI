import secrets  # Import the secrets module for generating a secure random key
DATABASE = "database.db"
SECRET  = secrets.token_hex(16)  # Generates a 32-character hex string  # Set a secret key for session management