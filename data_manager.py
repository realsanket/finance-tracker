# Handles loading and saving of financial data and prediction rules
import json
import os
import uuid

DATA_FILE = 'financial_data.json'
PREDICTION_RULES_FILE = 'prediction_rules.json'

def get_default_entry():
    return [{
        'GUID': str(uuid.uuid4()),
        'Date': '2025-05-09',
        'HDFC (₹)': 6357,
        'ICICI (₹)': 56752,
        'SBI (₹)': 81000,
        'SBI Overdraft (₹)': 815000,
        'OP (₹)': 117000,
        'Grow Stock (₹)': 20000,
        'Grow Mutual Funds (₹)': 203000,
        'Need to get': 443780,
        'Credit card+ other exp': 565000,
        'Total (₹)': 1177889,
        'OP (Euro)': 1300
    }]

def ensure_guids(data):
    changed = False
    for row in data:
        if 'GUID' not in row or not row['GUID']:
            row['GUID'] = str(uuid.uuid4())
            changed = True
    return changed

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return get_default_entry()

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_prediction_rules():
    if os.path.exists(PREDICTION_RULES_FILE):
        with open(PREDICTION_RULES_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default prediction rules if file doesn't exist
        default_rules = [
            {
                "id": "1",
                "day": 2,
                "month": None,
                "description": "Add ₹25,000 to SBI Overdraft",
                "account": "SBI Overdraft (₹)",
                "amount": 25000,
                "operation": "add"
            },
            {
                "id": "2",
                "day": 4,
                "month": None,
                "description": "Subtract ₹80,000 from SBI Overdraft",
                "account": "SBI Overdraft (₹)",
                "amount": 80000,
                "operation": "subtract"
            },
            {
                "id": "3",
                "day": 15,
                "month": None,
                "description": "Add €4,500 to OP (Euro)",
                "account": "OP (Euro)",
                "amount": 4500,
                "operation": "add"
            },
            {
                "id": "4",
                "day": 16,
                "month": 5,
                "description": "Subtract €1,200 from OP (Euro) for rent",
                "account": "OP (Euro)",
                "amount": 1200,
                "operation": "subtract"
            }
        ]
        save_prediction_rules(default_rules)
        return default_rules

def save_prediction_rules(rules):
    with open(PREDICTION_RULES_FILE, 'w') as f:
        json.dump(rules, f, indent=2)
