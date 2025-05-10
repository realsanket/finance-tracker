# Handles prediction logic and future event generation
import pandas as pd
from datetime import datetime, date
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app_config as config_module
SUPABASE_URL = config_module.SUPABASE_URL
SUPABASE_KEY = config_module.SUPABASE_KEY
from utils.utils import generate_uuid, load_json_file
from data_manager import load_prediction_rules

def generate_future_events(df, months_ahead=3, rules=None):
    if df.empty:
        return df
    if rules is None:
        rules = load_prediction_rules()
    last_date = pd.to_datetime(df['Date'].max())
    last_row = df[df['Date'] == df['Date'].max()].iloc[0].copy()
    account_values = {}
    for col in last_row.index:
        if isinstance(last_row[col], (int, float)) or (isinstance(last_row[col], str) and last_row[col].replace('.','',1).isdigit()):
            try:
                account_values[col] = float(last_row[col])
            except (ValueError, TypeError):
                account_values[col] = 0.0
    current_date = last_date
    events = []
    for m in range(months_ahead):
        for d in range(1, 32):
            try:
                day = date(current_date.year, current_date.month, d)
            except ValueError:
                continue
            if day <= last_date.date():
                continue
            for rule in rules:
                rule_day = rule.get('day')
                rule_month = rule.get('month')
                rule_account = rule.get('account')
                rule_amount = float(rule.get('amount', 0))
                rule_operation = rule.get('operation', 'add')
                rule_description = rule.get('description', '')
                if rule_day == day.day and (rule_month is None or rule_month == day.month):
                    event = {
                        'Date': day.strftime('%Y-%m-%d'),
                        'Event': rule_description
                    }
                    if rule_operation == 'add':
                        account_values[rule_account] = account_values.get(rule_account, 0) + rule_amount
                    else:
                        account_values[rule_account] = account_values.get(rule_account, 0) - rule_amount
                    account_values['OP (₹)'] = float(account_values.get('OP (Euro)', 0)) * 95
                    for account, value in account_values.items():
                        event[account] = value
                    if rule_amount != 0:
                        for account_col in ['HDFC (₹)', 'ICICI (₹)', 'SBI (₹)', 'SBI Overdraft (₹)', 'Grow Stock (₹)', 'Grow Mutual Funds (₹)', 'Need to get', 'Credit card+ other exp', 'OP (Euro)', 'OP (₹)']:
                            if account_col not in event or event[account_col] is None:
                                event[account_col] = 0.0
                        try:
                            event['Total (₹)'] = sum(float(event.get(col, 0)) for col in [
                                'HDFC (₹)', 'ICICI (₹)', 'SBI (₹)', 'SBI Overdraft (₹)', 
                                'Grow Stock (₹)', 'Grow Mutual Funds (₹)', 'Need to get', 'OP (₹)'
                            ]) - float(event.get('Credit card+ other exp', 0))
                        except Exception:
                            event['Total (₹)'] = 0.0
                        events.append(event)
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)
    return pd.DataFrame(events)
