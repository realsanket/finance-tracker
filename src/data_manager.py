from supabase import create_client, Client
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config as config_module
SUPABASE_URL = config_module.SUPABASE_URL
SUPABASE_KEY = config_module.SUPABASE_KEY
from utils.utils import generate_uuid, load_json_file, save_json_file

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Financial Data ---
def ensure_guids(data):
    changed = False
    for row in data:
        if not row.get("id"):
            row["id"] = generate_uuid()
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
            row["id"] = generate_uuid()
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
            rule["id"] = generate_uuid()
        supabase.table("prediction_rules").insert(rule).execute()

# --- Columns/Schema ---
COLUMNS_FILE = 'columns.json'
def load_columns():
    return load_json_file(COLUMNS_FILE)

def save_columns(columns):
    save_json_file(COLUMNS_FILE, columns)

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
