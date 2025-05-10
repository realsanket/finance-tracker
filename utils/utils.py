# Utility functions for the finance tracker project
import uuid
import json
import os

def generate_uuid():
    return str(uuid.uuid4())

def load_json_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []

def save_json_file(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
