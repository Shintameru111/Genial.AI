GENIAL.AI - STARTER IMPLEMENTATION

1. Copy folder app/ into your existing Genial.AI project (merge with your current app folder).
2. Keep data/ folder at the project root.
3. In VS Code terminal, activate your virtual environment.
4. Install dependencies:
   pip install -r requirements.txt
5. Run from the project root:
   python app/main.py

Database:
- SQLite database is created automatically at data/genial.db.
- Salon-wide capacity default: 3 concurrent appointments.
- Service capacities are seeded in app/database.py and can be changed in Admin menu.
- Opening/closing hours default to 09:00-21:00.
- Existing bookings.json is NOT automatically imported. Keep it as backup; do not delete it.

Calendar:
- ICS export works without Google credentials. Import data/exports/genial_bookings.ics into your calendar.
- Google sync is optional. Set up a Google Calendar API OAuth Desktop App, download the OAuth client JSON,
  rename it to credentials.json, and put it in the project root. Do not commit credentials.json or token.json.
- Google sync requires the Google dependencies in requirements.txt and a browser for OAuth consent.

Reports:
- Excel export requires openpyxl (included in requirements.txt).
- Exports are saved in data/exports/.

Capacity model:
- A booking consumes one salon-wide slot over its full appointment interval.
- Each selected service also consumes one unit of that service's capacity during its sequential service segment.
- This is a capacity model, not employee assignment. Employee-specific schedules are a later feature.
