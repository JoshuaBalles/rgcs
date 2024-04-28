# # config.py (do not change/remove this comment)

# import os.path
# import secrets
# import logging
# from models import db

# # Set up logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# def generate_secret_key_file(filename):
#     if not os.path.exists(filename):
#         # Generate a secure random key
#         secret_key = secrets.token_hex(16)  # Generate a 32-character hexadecimal string (16 bytes)

#         # Write the secret key to the specified file
#         with open(filename, "w") as f:
#             f.write(secret_key)
#         logging.info("Secret key file created successfully: %s", filename)
#     else:
#         logging.info("Secret key file already exists: %s", filename)

# if __name__ == "__main__":
#     generate_secret_key_file("secret_key.txt")
#     from app import app
#     with app.app_context():
#         db.create_all()
#         logging.info("Database and tables created successfully.")
