"""Configuration constants loaded from the environment.

All App Store Connect credentials are read from environment variables via
python-dotenv, which reads an optional `.env` file at the project root.
See `.env.example` for the required variables.
"""
import os

from dotenv import load_dotenv

load_dotenv()

KEY_ID = os.getenv("ASC_KEY_ID")
ISSUER_ID = os.getenv("ASC_ISSUER_ID")
PRIVATE_KEY_PATH = os.getenv(
    "ASC_PRIVATE_KEY_PATH", "AppStoreConnectAuthKey.p8")
EXPIRATION_MINUTES = int(os.getenv("ASC_EXPIRATION_MINUTES", "19"))
