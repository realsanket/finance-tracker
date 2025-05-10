from supabase import create_client, Client
import os
import uuid
import json

SUPABASE_URL = "https://apgbrhrovikixrjzwpvl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFwZ2JyaHJvdmlraXhyanp3cHZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY4NzUzMTIsImV4cCI6MjA2MjQ1MTMxMn0.X3EcU2SODXQ2IM71rjTSmgwtuewWgdjnmugCexELhNU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Financial Data ---
def ensure_guids(data):
    changed = False
    for row in data:
        if not row.get("id"):
            row["id"] = str(uuid.uuid4())
            changed = True
    return changed

def load_data():
    response = supabase.table("financial_data").select("*").execute()
    data = response.data
    # Map 'date' to 'Date' for compatibility with the rest of the app
    for row in data:
        if 'date' in row:
            row['Date'] = row.pop('date')
    return data

def save_data(data):
    supabase.table("financial_data").delete().not_.is_('id', None).execute()
    for row in data:
        # Ensure id is present
        if not row.get("id"):
            row["id"] = str(uuid.uuid4())
        # Map 'Date' to 'date' for Supabase
        row_to_insert = row.copy()
        if 'Date' in row_to_insert:
            row_to_insert['date'] = row_to_insert.pop('Date')
        # Remove GUID if present (Supabase does not have a GUID column)
        if 'GUID' in row_to_insert:
            del row_to_insert['GUID']
        supabase.table("financial_data").insert(row_to_insert).execute()

# --- Prediction Rules ---
def load_prediction_rules():
    response = supabase.table("prediction_rules").select("*").execute()
    return response.data

def save_prediction_rules(rules):
    supabase.table("prediction_rules").delete().not_.is_('id', None).execute()
    for rule in rules:
        if not rule.get("id"):
            rule["id"] = str(uuid.uuid4())
        supabase.table("prediction_rules").insert(rule).execute()

# --- Columns/Schema ---
COLUMNS_FILE = 'columns.json'
def load_columns():
    if os.path.exists(COLUMNS_FILE):
        with open(COLUMNS_FILE, 'r') as f:
            return json.load(f)
    else:
        return []

def save_columns(columns):
    with open(COLUMNS_FILE, 'w') as f:
        json.dump(columns, f, indent=2)

def add_column(column_name, operation="add", default_value=0):
    columns = load_columns()
    if not any(col["name"] == column_name for col in columns):
        columns.append({"name": column_name, "operation": operation})
        save_columns(columns)

def remove_column(column_name):
    columns = load_columns()
    columns = [col for col in columns if col["name"] != column_name]
    save_columns(columns)

def update_column_operation(column_name, operation):
    columns = load_columns()
    for col in columns:
        if col["name"] == column_name:
            col["operation"] = operation
    save_columns(columns)

def get_column_by_name(columns, name):
    for col in columns:
        if col["name"] == name:
            return col
    return None
