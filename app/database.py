from __future__ import annotations
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
DB_PATH = DATA / "genial.db"

DEFAULT_SERVICES = [
    ("Haircut", 50000, 30, 3), ("Haircut & Styling", 100000, 60, 2),
    ("Hair Coloring", 150000, 120, 2), ("Hair Highlights", 200000, 180, 1),
    ("Hair Wash", 30000, 20, 3), ("Hair Treatment", 100000, 60, 2),
    ("Manicure and Pedicure", 175000, 90, 2), ("Facial Treatment", 200000, 60, 2),
    ("Makeup Application", 250000, 60, 2), ("Bridal Makeup", 500000, 120, 1),
    ("Eyebrow Threading", 40000, 15, 2), ("Eyelash Extensions", 300000, 120, 1),
    ("Waxing", 80000, 30, 2), ("Skincare Consultation", 150000, 30, 2),
    ("Massage Therapy", 200000, 60, 2), ("bridal package", 1500000, 240, 1),
    ("spa package", 1000000, 120, 1), ("hair spa", 250000, 90, 2),
    ("nail art", 100000, 60, 2), ("bridal hair styling", 300000, 90, 1),
    ("bridal makeup trial", 200000, 90, 1), ("bridal hair trial", 150000, 90, 1),
    ("bridal package with makeup and hair", 2000000, 300, 1),
]

def connect():
    con = sqlite3.connect(DB_PATH, timeout=15)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA busy_timeout=15000")
    return con

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS services(
          id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, price INTEGER NOT NULL,
          duration_minutes INTEGER NOT NULL, capacity INTEGER NOT NULL DEFAULT 1,
          active INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS bookings(
          id INTEGER PRIMARY KEY, customer_name TEXT NOT NULL, phone TEXT,
          start_at TEXT NOT NULL, end_at TEXT NOT NULL, total_price INTEGER NOT NULL,
          status TEXT NOT NULL DEFAULT 'confirmed', notes TEXT, google_event_id TEXT,
          created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS booking_services(
          id INTEGER PRIMARY KEY, booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
          service_id INTEGER NOT NULL REFERENCES services(id), start_at TEXT NOT NULL,
          end_at TEXT NOT NULL, price INTEGER NOT NULL, duration_minutes INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS payments(
          id INTEGER PRIMARY KEY, booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
          amount INTEGER NOT NULL, method TEXT, status TEXT NOT NULL DEFAULT 'unpaid', paid_at TEXT);
        CREATE TABLE IF NOT EXISTS booking_history(
          id INTEGER PRIMARY KEY, booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
          action TEXT NOT NULL, details TEXT, created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_booking_times ON bookings(status,start_at,end_at);
        CREATE INDEX IF NOT EXISTS idx_service_times ON booking_services(service_id,start_at,end_at);
        """)
        for k,v in {"salon_name":"Glow Beauty Salon","salon_capacity":"3",
                    "opening_hour":"9","closing_hour":"21","timezone":"Asia/Jakarta",
                    "google_calendar_id":"primary"}.items():
            c.execute("INSERT OR IGNORE INTO settings VALUES(?,?)",(k,v))
        if c.execute("SELECT COUNT(*) FROM services").fetchone()[0] == 0:
            c.executemany("INSERT INTO services(name,price,duration_minutes,capacity) VALUES(?,?,?,?)", DEFAULT_SERVICES)

def setting(key, default=""):
    with connect() as c:
        row=c.execute("SELECT value FROM settings WHERE key=?",(key,)).fetchone()
        return row["value"] if row else default

def set_setting(key,value):
    with connect() as c:
        c.execute("""INSERT INTO settings VALUES(?,?) ON CONFLICT(key)
                     DO UPDATE SET value=excluded.value""",(key,str(value)))

def services(active=True):
    with connect() as c:
        q="SELECT * FROM services"+(" WHERE active=1" if active else "")+" ORDER BY name"
        return c.execute(q).fetchall()

def update_service_capacity(service_id, capacity):
    if capacity < 1: raise ValueError("Kapasitas minimal 1.")
    with connect() as c:
        cur=c.execute("UPDATE services SET capacity=? WHERE id=?",(capacity,service_id))
        if not cur.rowcount: raise ValueError("ID layanan tidak ditemukan.")

def _overlaps(c,start,end,service_id=None):
    a,b=start.isoformat(timespec="minutes"),end.isoformat(timespec="minutes")
    if service_id is None:
        row=c.execute("""SELECT COUNT(*) FROM bookings
          WHERE status='confirmed' AND start_at < ? AND end_at > ?""",(b,a)).fetchone()
    else:
        row=c.execute("""SELECT COUNT(*) FROM booking_services bs
          JOIN bookings b ON b.id=bs.booking_id
          WHERE b.status='confirmed' AND bs.service_id=?
          AND bs.start_at < ? AND bs.end_at > ?""",(service_id,b,a)).fetchone()
    return row[0]

def _validate(c,start,items):
    duration=sum(x["duration_minutes"] for x in items)
    end=start+timedelta(minutes=duration)
    op,cl=int(setting("opening_hour","9")),int(setting("closing_hour","21"))
    if start < start.replace(hour=op,minute=0,second=0,microsecond=0):
        return False,f"Salon baru buka pukul {op:02d}:00."
    if end > start.replace(hour=cl,minute=0,second=0,microsecond=0):
        return False,f"Booking harus selesai paling lambat pukul {cl:02d}:00."
    cap=int(setting("salon_capacity","1"))
    if _overlaps(c,start,end) >= cap:
        return False,f"Kapasitas salon penuh ({cap} slot)."
    cursor=start
    for x in items:
        finish=cursor+timedelta(minutes=x["duration_minutes"])
        if _overlaps(c,cursor,finish,x["id"]) >= x["capacity"]:
            return False,f"Kapasitas layanan {x['name']} penuh pada {cursor:%H:%M}–{finish:%H:%M}."
        cursor=finish
    return True,"Jadwal tersedia."

def check_availability(start,items):
    with connect() as c: return _validate(c,start,items)

def find_next_slot(start,items,days=30):
    op,cl=int(setting("opening_hour","9")),int(setting("closing_hour","21"))
    candidate=start.replace(second=0,microsecond=0)
    end_date=start.date()+timedelta(days=days)
    while candidate.date() <= end_date:
        opening=candidate.replace(hour=op,minute=0)
        closing=candidate.replace(hour=cl,minute=0)
        if candidate < opening: candidate=opening
        duration=sum(x["duration_minutes"] for x in items)
        if candidate+timedelta(minutes=duration)>closing:
            candidate=(candidate+timedelta(days=1)).replace(hour=op,minute=0)
            continue
        ok,_=check_availability(candidate,items)
        if ok: return candidate
        candidate+=timedelta(minutes=15)
    return None

def create_booking(name,phone,start,service_ids,notes=""):
    with connect() as c:
        c.execute("BEGIN IMMEDIATE")
        ids=list(service_ids)
        if not ids: raise ValueError("Pilih minimal satu layanan.")
        marks=",".join("?" for _ in ids)
        rows=c.execute(f"SELECT * FROM services WHERE active=1 AND id IN ({marks})",ids).fetchall()
        indexed={r["id"]:dict(r) for r in rows}
        if len(indexed)!=len(set(ids)): raise ValueError("Layanan tidak ditemukan/tidak aktif.")
        items=[indexed[i] for i in ids]
        ok,msg=_validate(c,start,items)
        if not ok: raise ValueError(msg)
        total=sum(x["price"] for x in items)
        duration=sum(x["duration_minutes"] for x in items)
        end=start+timedelta(minutes=duration)
        cur=c.execute("""INSERT INTO bookings(customer_name,phone,start_at,end_at,total_price,status,notes,created_at)
          VALUES(?,?,?,?,?,'confirmed',?,?)""",
          (name.strip(),phone.strip(),start.isoformat(timespec="minutes"),
           end.isoformat(timespec="minutes"),total,notes.strip(),datetime.now().isoformat(timespec="seconds")))
        bid=cur.lastrowid
        cursor=start
        for x in items:
            finish=cursor+timedelta(minutes=x["duration_minutes"])
            c.execute("""INSERT INTO booking_services(booking_id,service_id,start_at,end_at,price,duration_minutes)
              VALUES(?,?,?,?,?,?)""",(bid,x["id"],cursor.isoformat(timespec="minutes"),
              finish.isoformat(timespec="minutes"),x["price"],x["duration_minutes"]))
            cursor=finish
        c.execute("INSERT INTO booking_history(booking_id,action,details,created_at) VALUES(?,?,?,?)",
                  (bid,"created","Booking dikonfirmasi",datetime.now().isoformat(timespec="seconds")))
        return bid

def list_bookings():
    with connect() as c:
        return c.execute("""SELECT b.*, GROUP_CONCAT(s.name, ', ') services
          FROM bookings b LEFT JOIN booking_services bs ON bs.booking_id=b.id
          LEFT JOIN services s ON s.id=bs.service_id
          GROUP BY b.id ORDER BY b.start_at""").fetchall()

def cancel_booking(bid):
    with connect() as c:
        cur=c.execute("UPDATE bookings SET status='cancelled' WHERE id=? AND status='confirmed'",(bid,))
        if not cur.rowcount: raise ValueError("Booking aktif tidak ditemukan.")
        c.execute("INSERT INTO booking_history(booking_id,action,details,created_at) VALUES(?,?,?,?)",
                  (bid,"cancelled","Booking dibatalkan",datetime.now().isoformat(timespec="seconds")))

def report_rows(start_date=None,end_date=None):
    q="""SELECT b.id,b.customer_name,b.phone,b.start_at,b.end_at,b.total_price,b.status,
      GROUP_CONCAT(s.name, ', ') services FROM bookings b
      LEFT JOIN booking_services bs ON bs.booking_id=b.id
      LEFT JOIN services s ON s.id=bs.service_id"""
    cond=[]; args=[]
    if start_date: cond.append("date(b.start_at)>=date(?)"); args.append(start_date)
    if end_date: cond.append("date(b.start_at)<=date(?)"); args.append(end_date)
    if cond: q+=" WHERE "+" AND ".join(cond)
    q+=" GROUP BY b.id ORDER BY b.start_at"
    with connect() as c: return c.execute(q,args).fetchall()


def get_booking_details(booking_id):
    with connect() as c:
        booking = c.execute(
            "SELECT * FROM bookings WHERE id = ?", (booking_id,)
        ).fetchone()
        if booking is None:
            return None
        items = c.execute("""
            SELECT s.name, bs.start_at, bs.end_at, bs.price, bs.duration_minutes
            FROM booking_services bs
            JOIN services s ON s.id = bs.service_id
            WHERE bs.booking_id = ?
            ORDER BY bs.start_at
        """, (booking_id,)).fetchall()
        return {"booking": dict(booking), "services": [dict(x) for x in items]}
