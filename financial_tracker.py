import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
import uuid

# Import business logic modules
from data_manager import load_data, save_data, ensure_guids, load_prediction_rules, save_prediction_rules
from prediction import generate_future_events

# File to persist data
DATA_FILE = 'financial_data.json'
PREDICTION_RULES_FILE = 'prediction_rules.json'

# Default initial entry
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

def main():
    # Set Streamlit page config for wide layout
    st.set_page_config(layout="wide")

    # --- Centered and styled title ---
    st.markdown(
        """
        <h1 style='text-align: center; color: #2E86C1; font-size: 3em; font-family: "Segoe UI", Arial, sans-serif; margin-bottom: 0.2em; margin-top: 0;'>
            Financial Event Tracker
        </h1>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<hr style='margin-top:0;margin-bottom:1.5em;border:1px solid #2E86C1;'>", unsafe_allow_html=True)

    # Load data
    data = load_data()
    if ensure_guids(data):
        save_data(data)
    df = pd.DataFrame(data)
    
    # Load prediction rules
    prediction_rules = load_prediction_rules()

    # Ensure Date is always the second column for display and sort by Date descending
    if 'Date' in df.columns:
        cols = [col for col in df.columns if col not in ['GUID', 'Date']]
        df = df.sort_values('Date', ascending=False)
        display_cols = ['Date'] + cols
        display_df = df[display_cols].copy()
    else:
        display_df = df.copy()

    # --- Future Mode & Rules Mode Switch ---
    col1, col2 = st.columns(2)
    with col1:
        future_mode = st.toggle('🔮 Future Mode', value=False, help='Switch to see future predictions based on recurring events')
    with col2:
        rules_mode = st.toggle('⚙️ Prediction Rules', value=False, help='View and edit prediction rules for recurring events')

    # --- User selection for months ahead in future mode ---
    months_ahead = 3
    if future_mode:
        months_ahead = st.slider('How many months ahead to generate predictions?', min_value=1, max_value=12, value=3, step=1)
    
    # --- Prediction Rules Management UI ---
    if rules_mode:
        st.markdown(
            """
            <h2 style='text-align:center; color:#8E44AD; font-family: "Segoe UI", Arial, sans-serif; margin-bottom: 0.5em;'>
                Prediction Rules Manager
            </h2>
            """,
            unsafe_allow_html=True
        )
        
        # Display existing rules in a table
        rules_df = pd.DataFrame(prediction_rules)
        
        # Format the month column to handle None, NaN, or empty string values
        def format_month(x):
            if x is None:
                return 'Any'
            if isinstance(x, float) and pd.isna(x):
                return 'Any'
            if isinstance(x, str) and x.strip().lower() in ('', 'nan', 'none'):
                return 'Any'
            try:
                month_int = int(float(x))
                return datetime(2000, month_int, 1).strftime('%B')
            except Exception:
                return str(x)
        rules_df['month'] = rules_df['month'].apply(format_month)
        
        # Reorder and rename columns for display
        display_cols = ['id', 'description', 'account', 'amount', 'operation', 'day', 'month']
        display_names = {'id': 'ID', 'description': 'Description', 'account': 'Account', 
                        'amount': 'Amount', 'operation': 'Operation', 'day': 'Day', 'month': 'Month'}
        
        # Display rules table
        st.dataframe(
            rules_df[display_cols].rename(columns=display_names),
            use_container_width=True,
            hide_index=True,
        )
        
        # Add new rule or edit existing rule
        st.markdown("### Add/Edit Prediction Rule")
        
        # Select existing rule to edit or create new
        rule_ids = ["New Rule"] + [rule["id"] for rule in prediction_rules]
        selected_rule_id = st.selectbox("Select a rule to edit or 'New Rule' to create", options=rule_ids)
        
        # Pre-fill form if editing existing rule
        if selected_rule_id != "New Rule":
            rule = next((r for r in prediction_rules if r["id"] == selected_rule_id), None)
            if rule:
                edit_mode = True
                rule_id = rule["id"]
                description = rule["description"]
                account = rule["account"]
                amount = rule["amount"]
                operation = rule["operation"]
                day = rule["day"]
                month = rule["month"] if rule["month"] is not None else ""
            else:
                st.error("Rule not found!")
                edit_mode = False
                rule_id = str(len(prediction_rules) + 1)
                description = ""
                account = "SBI Overdraft (₹)"
                amount = 0
                operation = "add"
                day = 1
                month = ""
        else:
            edit_mode = False
            rule_id = str(len(prediction_rules) + 1)
            description = ""
            account = "SBI Overdraft (₹)"
            amount = 0
            operation = "add"
            day = 1
            month = ""
        
        # Rule editing form
        with st.form("rule_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                description = st.text_input("Description", value=description)
                account = st.selectbox(
                    "Account", 
                    options=["SBI Overdraft (₹)", "OP (Euro)", "HDFC (₹)", "ICICI (₹)", "SBI (₹)", 
                            "Grow Stock (₹)", "Grow Mutual Funds (₹)", "Need to get", "Credit card+ other exp"],
                    index=0 if account == "SBI Overdraft (₹)" else (1 if account == "OP (Euro)" else 0),
                )
                amount = st.number_input("Amount", value=float(amount), min_value=0.0)
            
            with col2:
                operation = st.selectbox("Operation", options=["add", "subtract"], index=0 if operation == "add" else 1)
                day = st.number_input("Day of Month", value=int(day), min_value=1, max_value=31)
                month_input = st.text_input("Month (leave blank for every month, or enter number 1-12)", value=month)
                
            submit_rule = st.form_submit_button("Save Rule")
            
            if submit_rule:
                # Validate inputs
                try:
                    # Process month field (empty = None, otherwise numeric 1-12)
                    if month_input.strip() == "":
                        month_value = None
                    else:
                        month_value = int(month_input.strip())
                        if month_value < 1 or month_value > 12:
                            st.error("Month must be between 1 and 12")
                            month_value = None
                    
                    new_rule = {
                        "id": rule_id,
                        "day": day,
                        "month": month_value,
                        "description": description,
                        "account": account,
                        "amount": amount,
                        "operation": operation
                    }
                    
                    # Update or add the rule
                    if edit_mode:
                        for i, rule in enumerate(prediction_rules):
                            if rule["id"] == rule_id:
                                prediction_rules[i] = new_rule
                                break
                    else:
                        prediction_rules.append(new_rule)
                    
                    save_prediction_rules(prediction_rules)
                    st.success("Rule saved successfully!")
                    try:
                        st.rerun()
                    except AttributeError:
                        try:
                            st.experimental_rerun()
                        except AttributeError:
                            st.warning('Please update your Streamlit version to enable auto-refresh after saving a rule.')
                    
                except Exception as e:
                    st.error(f"Error saving rule: {e}")
        
        # Delete rule
        st.markdown("### Delete Rule")
        rule_to_delete = st.selectbox("Select a rule to delete", options=["None"] + [f"{rule['id']}: {rule['description']}" for rule in prediction_rules])
        
        if rule_to_delete != "None" and st.button("Delete Rule"):
            delete_id = rule_to_delete.split(":")[0].strip()
            prediction_rules = [rule for rule in prediction_rules if rule["id"] != delete_id]
            save_prediction_rules(prediction_rules)
            st.success("Rule deleted successfully!")
            try:
                st.rerun()
            except AttributeError:
                try:
                    st.experimental_rerun()
                except AttributeError:
                    st.warning('Please update your Streamlit version to enable auto-refresh after deleting a rule.')
    
    # --- Prediction Logic Summary ---
    if future_mode:
        # Generate prediction summary dynamically from rules
        prediction_html = '''
        <div style="background-color:#F4ECF7; border-radius:10px; padding:1em; margin-bottom:1em;">
        <h4 style="color:#8E44AD;">Prediction Logic</h4>
        <ul style="font-size:1.1em;">
        '''
        
        for rule in prediction_rules:
            # Skip rules with amount 0
            if float(rule.get("amount", 0)) == 0:
                continue
            # Format day/month
            month_val = rule.get("month", None)
            # Handle None, NaN, and string 'nan' as 'Any'
            is_any_month = (
                month_val is None or
                (isinstance(month_val, float) and pd.isna(month_val)) or
                (isinstance(month_val, str) and month_val.strip().lower() in ["", "nan", "none"])
            )
            if is_any_month:
                day_prefix = f"Every {int(rule['day'])} of the month"
            else:
                try:
                    month_int = int(float(month_val))
                    month_name = datetime(2000, month_int, 1).strftime('%B')
                    day_prefix = f"On {month_name} {int(rule['day'])}"
                except Exception:
                    day_prefix = f"On month {month_val} {int(rule['day'])}"
            # Format action and currency
            amount_val = rule['amount']
            account = rule['account']
            if 'Euro' in account:
                amount_str = f"€{amount_val:,.0f}"
            else:
                amount_str = f"₹{amount_val:,.0f}"
            if rule["operation"] == "add":
                action = f"Add {amount_str} to {account}"
            else:
                action = f"Subtract {amount_str} from {account}"
            prediction_html += f'<li><b>{day_prefix}</b>: {action}.</li>'
        
        prediction_html += '''
        </ul>
        </div>
        '''
        
        st.markdown(prediction_html, unsafe_allow_html=True)

    # --- Table Display Logic ---
    if future_mode:
        # Show current event if today is an event day
        last_date = pd.to_datetime(df['Date'].max())
        last_row = df[df['Date'] == df['Date'].max()].iloc[0].copy()
        today = date.today()
        current_event = None
        
        # Create a dictionary to track account values
        account_values = {}
        for col in last_row.index:
            if isinstance(last_row[col], (int, float)) or (isinstance(last_row[col], str) and str(last_row[col]).replace('.','',1).isdigit()):
                try:
                    account_values[col] = float(last_row[col])
                except (ValueError, TypeError):
                    account_values[col] = 0.0
        
        # Check if any rules apply to today
        for rule in prediction_rules:
            rule_day = rule.get('day')
            rule_month = rule.get('month')
            rule_account = rule.get('account')
            rule_amount = float(rule.get('amount', 0))
            rule_operation = rule.get('operation', 'add')
            rule_description = rule.get('description', '')
            
            # Check if rule applies to today
            if rule_day == today.day and (rule_month is None or rule_month == today.month):
                # Create a new event
                current_event = {
                    'Date': today.strftime('%Y-%m-%d'),
                    'Event': rule_description
                }
                
                # Apply operation to account
                if rule_operation == 'add':
                    account_values[rule_account] = account_values.get(rule_account, 0) + rule_amount
                else:  # subtract
                    account_values[rule_account] = account_values.get(rule_account, 0) - rule_amount
                
                # Add all account values to the event
                for account, value in account_values.items():
                    current_event[account] = value
                
                # Add derived values
                if 'OP (Euro)' in account_values:
                    current_event['OP (₹)'] = account_values['OP (Euro)'] * 95
                    
                break  # Only show first event if multiple occur on the same day
                
        if current_event:
            st.markdown('<h4 style="color:#8E44AD;">Current Event</h4>', unsafe_allow_html=True)
            st.table(pd.DataFrame([current_event]))
        # Show only event rows in future, plus one day before and after each event
        future_events_df = generate_future_events(df, months_ahead=months_ahead, rules=prediction_rules)
        if not future_events_df.empty:
            # Get all event dates
            event_dates = pd.to_datetime(future_events_df['Date'])
            # Build set of days to show: event day, day before, day after
            days_to_show = set()
            for d in event_dates:
                days_to_show.add(d)
                days_to_show.add(d - pd.Timedelta(days=1))
            # Build a DataFrame for all days in the range
            min_day = min(days_to_show)
            max_day = max(days_to_show)
            all_days = pd.date_range(min_day, max_day)
            
            # Define all_columns before using it
            all_columns = list(df.columns) + ['Event']
            
            # For each day, if it's an event, use event row; else, fill with previous values
            rows = []
            prev_row = {}
            # Initialize prev_row with all scalar values from last_row
            for col in all_columns:
                if col in last_row:
                    # Convert any complex values to simple types
                    if isinstance(last_row[col], (list, dict)):
                        prev_row[col] = str(last_row[col])
                    else:
                        # Ensure numbers are float or int
                        if '₹' in col or 'Euro' in col or col == 'Total (₹)':
                            try:
                                prev_row[col] = float(last_row[col])
                            except (ValueError, TypeError):
                                prev_row[col] = 0.0
                        else:
                            prev_row[col] = last_row[col]
            prev_row['Date'] = last_date.strftime('%Y-%m-%d')
            prev_row['Event'] = ''
            
            for day in all_days:
                str_day = day.strftime('%Y-%m-%d')
                if str_day in future_events_df['Date'].values:
                    event_row = future_events_df[future_events_df['Date'] == str_day].iloc[0].to_dict()
                    # Create a new row with all scalar values
                    full_row = {}
                    # First copy previous values
                    for col in all_columns:
                        if col in prev_row:
                            full_row[col] = prev_row[col]
                        else:
                            full_row[col] = 0 if '₹' in col or 'Euro' in col or col == 'Total (₹)' else ''
                    # Then update with event values
                    for col, val in event_row.items():
                        if isinstance(val, (list, dict)):
                            full_row[col] = str(val)
                        else:
                            full_row[col] = val
                    # Always recalculate OP (₹) as OP (Euro) × 95 in the prediction table
                    full_row['OP (₹)'] = float(full_row.get('OP (Euro)', 0)) * 95
                    prev_row = full_row.copy()
                else:
                    # Non-event: carry forward previous values, update date and clear event
                    full_row = prev_row.copy()
                    full_row['Date'] = str_day
                    full_row['Event'] = ''
                    # Always recalculate OP (₹) as OP (Euro) × 95 in the prediction table
                    full_row['OP (₹)'] = float(full_row.get('OP (Euro)', 0)) * 95
                # Recalculate Total (₹)
                try:
                    full_row['Total (₹)'] = sum(float(full_row.get(col, 0)) for col in [
                        'HDFC (₹)', 'ICICI (₹)', 'SBI (₹)', 'SBI Overdraft (₹)', 
                        'Grow Stock (₹)', 'Grow Mutual Funds (₹)', 'Need to get', 'OP (₹)'
                    ]) - float(full_row.get('Credit card+ other exp', 0))
                except (ValueError, TypeError):
                    full_row['Total (₹)'] = 0.0
                rows.append(full_row)
                
            # Final validation of data before creating DataFrame
            clean_rows = []
            for row in rows:
                clean_row = {}
                for col in all_columns:
                    if col not in row:
                        clean_row[col] = 0 if '₹' in col or 'Euro' in col or col == 'Total (₹)' else ''
                    elif isinstance(row[col], (list, dict, pd.Series)):
                        clean_row[col] = str(row[col])
                    else:
                        clean_row[col] = row[col]
                clean_rows.append(clean_row)
            
            # Now create the DataFrame with clean data
            filtered_df = pd.DataFrame(clean_rows)
            filtered_df = filtered_df[filtered_df['Date'].isin([d.strftime('%Y-%m-%d') for d in sorted(days_to_show)])]
            # Reorder columns to match main table
            display_cols = [col for col in df.columns if col != 'GUID'] + ['Event']
            display_cols = [col for col in display_cols if col in filtered_df.columns]
            filtered_df = filtered_df[display_cols]
            st.markdown(f'<h3 style="text-align:center; color:#8E44AD;">Upcoming Financial Events (Next {months_ahead} Month{"s" if months_ahead > 1 else ""})</h3>', unsafe_allow_html=True)
            # --- Export to Excel button ---
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Predictions')
            excel_data = output.getvalue()
            st.download_button(
                label="Export to Excel",
                data=excel_data,
                file_name=f"future_predictions_{months_ahead}_months.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download the future prediction table as an Excel file."
            )
            st.dataframe(filtered_df, use_container_width=True, height=400, hide_index=True)
        else:
            st.info('No future events to display.')
    else:
        # Divide screen into two columns: left (table), right (add entry)
        left, right = st.columns([2, 1])
        with left:
            st.markdown(
                """
                <h2 style='text-align:center; color:#117A65; font-family: "Segoe UI", Arial, sans-serif; margin-bottom: 0.5em;'>Financial Data Table</h2>
                """,
                unsafe_allow_html=True
            )

            # --- Enhanced UX: Click table row to prefill Add New Entry form ---
            selected_idx = st.selectbox(
                'Click a row to prefill the Add New Entry form:',
                options=[None] + list(df.index),
                format_func=lambda x: f"{df.loc[x, 'Date']} | ₹{df.loc[x, 'Total (₹)']:,}" if x is not None else '-- Select a row --'
            )
            if selected_idx is not None:
                prefill_entry = df.loc[selected_idx].to_dict()
            else:
                prefill_entry = data[-1] if data else {}

            st.dataframe(
                display_df,
                use_container_width=True,
                height=400,
                hide_index=True,
            )
            st.markdown("<hr style='margin-top:1em;margin-bottom:1em;'>", unsafe_allow_html=True)
            # --- Action button below the table ---
            st.markdown("<div style='height: 0.5em'></div>", unsafe_allow_html=True)
            btn_col = st.columns(1)[0]
            with btn_col:
                if 'show_delete' not in st.session_state:
                    st.session_state['show_delete'] = False
                if st.button('🗑️ Show Delete Options', help='Show/hide delete options', key='show_delete_btn'):
                    st.session_state['show_delete'] = not st.session_state['show_delete']
            if st.session_state['show_delete']:
                st.markdown(
                    """
                    <div style='background-color:#FDEDEC; border-radius:10px; padding:1em 1em 0.5em 1em; margin-bottom:1em;'>
                        <h3 style='text-align:center; color:#C0392B; font-family: "Segoe UI", Arial, sans-serif; margin-top:0;'>🗑️ Delete Records</h3>
                        <p style='text-align:center; color:#922B21; font-size:1.1em;'>Select rows to delete:</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                selected_indices = []
                for i, row in df.iterrows():
                    checked = st.checkbox(f"🗂️ {row['Date']} | ₹{row['Total (₹)']:,}", key=f'select_{i}', value=False, help='Select to delete')
                    if checked:
                        selected_indices.append(i)
                if selected_indices:
                    st.markdown(f"<p style='color:#C0392B; text-align:center; font-weight:bold;'>Selected: {len(selected_indices)} row(s)</p>", unsafe_allow_html=True)
                if selected_indices and st.button('❌ Delete Selected Rows', key='delete_selected_btn', help='Delete selected rows'):
                    for idx in sorted(selected_indices, reverse=True):
                        data.pop(idx)
                    save_data(data)
                    st.session_state['show_delete'] = False
                    try:
                        st.rerun()
                    except AttributeError:
                        try:
                            st.experimental_rerun()
                        except AttributeError:
                            st.warning('Please update your Streamlit version to enable auto-refresh after deleting an entry.')

            # --- Update functionality ---
            st.markdown("<div style='height: 0.5em'></div>", unsafe_allow_html=True)
            if 'update_row' not in st.session_state:
                st.session_state['update_row'] = None
            # Use selectbox for update row selection
            update_idx = st.selectbox(
                'Select a row to update:',
                options=[None] + list(df.index),
                format_func=lambda x: f"{df.loc[x, 'Date']} | ₹{df.loc[x, 'Total (₹)']:,}" if x is not None else '-- Select a row --',
                key='update_row_selectbox'
            )
            if update_idx is not None:
                row = df.loc[update_idx]
                st.markdown(f"<h4 style='text-align:center; color:#148F77;'>Editing: {row['Date']} | ₹{row['Total (₹)']:,}</h4>", unsafe_allow_html=True)
                # Show compact update form (side-by-side like Add New Entry)
                h1, h2 = st.columns(2)
                # Use st.session_state to get the latest value for OP (Euro) for live calculation
                op_euro_key = f'update_op_euro_{update_idx}_form'
                # --- Live input fields (outside form for instant update) ---
                with h1:
                    hdfc = st.number_input('HDFC (₹)', min_value=0, value=int(row['HDFC (₹)']), key=f'update_hdfc_{update_idx}_form')
                    sbi = st.number_input('SBI (₹)', min_value=0, value=int(row['SBI (₹)']), key=f'update_sbi_{update_idx}_form')
                    grow_stock = st.number_input('Grow Stock (₹)', min_value=0, value=int(row['Grow Stock (₹)']), key=f'update_grow_stock_{update_idx}_form')
                    need_to_get = st.number_input('Need to get', min_value=0, value=int(row['Need to get']), key=f'update_need_to_get_{update_idx}_form')
                    op_euro = st.number_input('OP (Euro)', min_value=0, value=int(row['OP (Euro)']), key=op_euro_key)
                with h2:
                    icici = st.number_input('ICICI (₹)', min_value=0, value=int(row['ICICI (₹)']), key=f'update_icici_{update_idx}_form')
                    sbi_od = st.number_input('SBI Overdraft (₹)', min_value=0, value=int(row['SBI Overdraft (₹)']), key=f'update_sbi_od_{update_idx}_form')
                    grow_mf = st.number_input('Grow Mutual Funds (₹)', min_value=0, value=int(row['Grow Mutual Funds (₹)']), key=f'update_grow_mf_{update_idx}_form')
                    cc_exp = st.number_input('Credit card+ other exp', min_value=0, value=int(row['Credit card+ other exp']), key=f'update_cc_exp_{update_idx}_form')
                # Get the latest value for OP (Euro) from session state for live calculation
                op_euro_val = st.session_state.get(op_euro_key, op_euro)
                op_inr = float(op_euro_val) * 95
                st.markdown(f"**OP (₹):** {op_inr}")
                total = (
                    float(hdfc) + float(icici) + float(sbi) + float(sbi_od) + float(grow_stock) + float(grow_mf) + float(need_to_get) + op_inr - float(cc_exp)
                )
                st.markdown(f"**Total (₹):** {total}")
                # --- Form for submission only ---
                with st.form(f'update_form_{update_idx}', clear_on_submit=False):
                    date_val = st.date_input('Date', value=datetime.strptime(row['Date'], '%Y-%m-%d').date(), key=f'update_date_{update_idx}')
                    submitted = st.form_submit_button('💾 Update Entry')
                    if submitted:
                        updated_entry = {
                            'GUID': row['GUID'],  # Preserve GUID
                            'Date': date_val.strftime('%Y-%m-%d'),
                            'HDFC (₹)': float(hdfc),
                            'ICICI (₹)': float(icici),
                            'SBI (₹)': float(sbi),
                            'SBI Overdraft (₹)': float(sbi_od),
                            'Grow Stock (₹)': float(grow_stock),
                            'Grow Mutual Funds (₹)': float(grow_mf),
                            'Need to get': float(need_to_get),
                            'Credit card+ other exp': float(cc_exp),
                            'OP (Euro)': float(op_euro_val),
                            'OP (₹)': op_inr,
                            'Total (₹)': total
                        }
                        data[update_idx] = updated_entry
                        save_data(data)
                        try:
                            st.rerun()
                        except AttributeError:
                            try:
                                st.experimental_rerun()
                            except AttributeError:
                                st.warning('Please update your Streamlit version to enable auto-refresh after updating an entry.')

        with right:
            st.markdown(
                """
                <h2 style='text-align:center; color:#117A65; font-family: "Segoe UI", Arial, sans-serif; margin-bottom: 0.5em;'>Add New Entry</h2>
                """,
                unsafe_allow_html=True
            )
            last_entry = prefill_entry if prefill_entry else {}
            date_val = st.date_input('Date', value=datetime.strptime(last_entry.get('Date', str(date.today())), '%Y-%m-%d').date(), key='date')
            h1, h2 = st.columns(2)
            with h1:
                hdfc = st.number_input('HDFC (₹)', min_value=0, value=int(last_entry.get('HDFC (₹)', 0)), key='hdfc')
                sbi = st.number_input('SBI (₹)', min_value=0, value=int(last_entry.get('SBI (₹)', 0)), key='sbi')
                grow_stock = st.number_input('Grow Stock (₹)', min_value=0, value=int(last_entry.get('Grow Stock (₹)', 0)), key='grow_stock')
                need_to_get = st.number_input('Need to get', min_value=0, value=int(last_entry.get('Need to get', 0)), key='need_to_get')
                op_euro = st.number_input('OP (Euro)', min_value=0, value=int(last_entry.get('OP (Euro)', 0)), key='op_euro')
            with h2:
                icici = st.number_input('ICICI (₹)', min_value=0, value=int(last_entry.get('ICICI (₹)', 0)), key='icici')
                sbi_od = st.number_input('SBI Overdraft (₹)', min_value=0, value=int(last_entry.get('SBI Overdraft (₹)', 0)), key='sbi_od')
                grow_mf = st.number_input('Grow Mutual Funds (₹)', min_value=0, value=int(last_entry.get('Grow Mutual Funds (₹)', 0)), key='grow_mf')
                cc_exp = st.number_input('Credit card+ other exp', min_value=0, value=int(last_entry.get('Credit card+ other exp', 0)), key='cc_exp')
            op_inr = op_euro * 95
            st.markdown(f"**OP (₹):** {op_inr}")
            total = (
                hdfc + icici + sbi + sbi_od + grow_stock + grow_mf + need_to_get + op_inr - cc_exp
            )
            st.markdown(f"**Total (₹):** {total}")
            submitted = st.button('Add Entry')
            if submitted:
                entry = {
                    'GUID': str(uuid.uuid4()),
                    'Date': date_val.strftime('%Y-%m-%d'),
                    'HDFC (₹)': hdfc,
                    'ICICI (₹)': icici,
                    'SBI (₹)': sbi,
                    'SBI Overdraft (₹)': sbi_od,
                    'Grow Stock (₹)': grow_stock,
                    'Grow Mutual Funds (₹)': grow_mf,
                    'Need to get': need_to_get,
                    'Credit card+ other exp': cc_exp,
                    'OP (Euro)': op_euro,
                    'OP (₹)': op_inr,
                    'Total (₹)': total
                }
                data.append(entry)
                save_data(data)
                try:
                    st.rerun()
                except AttributeError:
                    try:
                        st.experimental_rerun()
                    except AttributeError:
                        st.warning('Please update your Streamlit version to enable auto-refresh after adding an entry.')

if __name__ == '__main__':
    main()
