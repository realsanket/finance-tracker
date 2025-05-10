# This file should be used to store configuration and secrets securely.
# Never commit real secrets to source control!
import os

# Best Practice: Load secrets from environment variables, not hardcoded values.
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set as environment variables.\n"
        "Example (in your shell):\n"
        "export SUPABASE_URL='your_supabase_url'\n"
        "export SUPABASE_KEY='your_supabase_key'"
    )
