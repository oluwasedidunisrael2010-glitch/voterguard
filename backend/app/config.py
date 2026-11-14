
"""Application settings."""
import os

def get_settings() -> dict:
    origins = os.environ.get(
        "CORS_ORIGINS",
        "https://voterguard.vercel.app,http://localhost:3000"
    )

    return {
        "db_path": os.environ.get("VOTERGUARD_DB", "data/voterguard.db"),
        "max_upload_bytes": int(
            float(os.environ.get("MAX_UPLOAD_MB", "5")) * 1024 * 1024
        ),
        "cors_origins": [o.strip() for o in origins.split(",") if o.strip()],
        "turso_database_url": os.environ.get("TURSO_DATABASE_URL"),
        "turso_auth_token": os.environ.get("TURSO_AUTH_TOKEN"),
    }
