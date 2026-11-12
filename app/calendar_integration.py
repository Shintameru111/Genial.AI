from datetime import datetime
from pathlib import Path
import os
import database as db

ROOT=Path(__file__).resolve().parent.parent
EXPORT_DIR=ROOT/"data"/"exports"
EXPORT_DIR.mkdir(parents=True,exist_ok=True)

def _escape(text):
    return str(text or "").replace("\\","\\\\").replace(";","\\;").replace(",","\\,").replace("\n","\\n")

def export_ics():
    rows=db.list_bookings()
    lines=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Genial.AI//Salon Booking//EN","CALSCALE:GREGORIAN"]
    for b in rows:
        if b["status"]!="confirmed": continue
        start=datetime.fromisoformat(b["start_at"])
        end=datetime.fromisoformat(b["end_at"])
        lines += [
            "BEGIN:VEVENT",
            f"UID:genial-booking-{b['id']}@genial.ai",
            f"DTSTAMP:{datetime.utcnow():%Y%m%dT%H%M%SZ}",
            f"DTSTART:{start:%Y%m%dT%H%M%S}",
            f"DTEND:{end:%Y%m%dT%H%M%S}",
            f"SUMMARY:{_escape('Booking - '+b['customer_name'])}",
            f"DESCRIPTION:{_escape('Layanan: '+str(b['services'])+' | Status: '+b['status'])}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    path=EXPORT_DIR/"genial_bookings.ics"
    path.write_text("\r\n".join(lines)+"\r\n",encoding="utf-8")
    return path

def sync_booking_to_google(booking_id):
    """Optional Google Calendar sync. Requires OAuth libraries and credentials.json."""
    credentials_file=ROOT/"credentials.json"
    if not credentials_file.exists():
        return None
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError("Install dependensi Google Calendar dari requirements.txt.") from exc

    token_file=ROOT/"token.json"
    scopes=["https://www.googleapis.com/auth/calendar.events"]
    creds=None
    if token_file.exists():
        creds=Credentials.from_authorized_user_file(str(token_file),scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow=InstalledAppFlow.from_client_secrets_file(str(credentials_file),scopes)
            creds=flow.run_local_server(port=0)
        token_file.write_text(creds.to_json(),encoding="utf-8")

    details=db.get_booking_details(booking_id)
    if not details: raise RuntimeError("Booking tidak ditemukan.")
    b=details["booking"]
    service=build("calendar","v3",credentials=creds)
    event={
        "summary":f"Genial.AI - {b['customer_name']}",
        "description":"Services: "+", ".join(x["name"] for x in details["services"]),
        "start":{"dateTime":datetime.fromisoformat(b["start_at"]).isoformat(),"timeZone":"Asia/Jakarta"},
        "end":{"dateTime":datetime.fromisoformat(b["end_at"]).isoformat(),"timeZone":"Asia/Jakarta"},
    }
    result=service.events().insert(
        calendarId=db.setting("google_calendar_id","primary"),body=event
    ).execute()
    with db.connect() as con:
        con.execute("UPDATE bookings SET google_event_id=? WHERE id=?",(result.get("id"),booking_id))
    return result.get("id")
