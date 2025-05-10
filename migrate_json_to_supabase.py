import json
from supabase import create_client, Client
import uuid

SUPABASE_URL = "https://apgbrhrovikixrjzwpvl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFwZ2JyaHJvdmlraXhyanp3cHZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY4NzUzMTIsImV4cCI6MjA2MjQ1MTMxMn0.X3EcU2SODXQ2IM71rjTSmgwtuewWgdjnmugCexELhNU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

with open("financial_data.json") as f:
    data = json.load(f)
    for row in data:
        if not row.get("id"):
            row["id"] = str(uuid.uuid4())
        supabase.table("financial_data").insert(row).execute()

with open("prediction_rules.json") as f:
    rules = json.load(f)
    for rule in rules:
        if not rule.get("id"):
            rule["id"] = str(uuid.uuid4())
        supabase.table("prediction_rules").insert(rule).execute()
