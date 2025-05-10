# Financial Event Tracker

A Streamlit web app to track financial events, add entries, export data, and predict future values.

## Features
- Load and save financial data from/to JSON
- Add new entries via a form
- Export data to CSV/Excel
- Date range filters and summary statistics
- Customizable prediction rules for recurring events
- Predict future values for key dates based on custom rules
- Data persists across sessions

## Setup

1. **Clone or download this repository.**
2. **Create and activate a virtual environment:**
   ```zsh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```zsh
   pip install -r requirements.txt
   ```
4. **Run the Streamlit app:**
   ```zsh
   streamlit run financial_tracker.py
   ```

## Usage
- Use the web interface to view, add, and export financial data.
- Use the "⚙️ Prediction Rules" toggle to add, edit, or delete prediction rules.
- Use the "🔮 Future Mode" toggle to see future predictions based on your rules.
- Financial data is saved in `financial_data.json` for persistence.
- Prediction rules are saved in `prediction_rules.json`.

---

*Developed with Python, Streamlit, and Pandas.*

