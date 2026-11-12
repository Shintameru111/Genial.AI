from datetime import datetime
import database as db
from calendar_integration import export_ics, sync_booking_to_google
from reports import export_excel

def rupiah(value):
    return "Rp " + f"{value:,}".replace(",", ".")

def choose_services():
    rows=db.services()
    print("\n========== AVAILABLE SERVICES ==========")
    for i,s in enumerate(rows,1):
        print(f"{i}. {s['name']} | {rupiah(s['price'])} | {s['duration_minutes']} menit | kapasitas {s['capacity']}")
    raw=input("\nPilih nomor layanan (pisahkan koma, contoh 1,3): ").strip()
    try:
        nums=[int(x.strip()) for x in raw.split(",")]
        if not nums or len(nums)!=len(set(nums)) or any(n<1 or n>len(rows) for n in nums):
            raise ValueError
        return [dict(rows[n-1]) for n in nums]
    except ValueError:
        print("Pilihan tidak valid. Coba lagi.")
        return None

def make_booking():
    op,cl=int(db.setting("opening_hour","9")),int(db.setting("closing_hour","21"))
    print(f"\nJam operasional {db.setting('salon_name','Glow Beauty Salon')}: {op:02d}:00–{cl:02d}:00")
    print(f"Kapasitas salon: {db.setting('salon_capacity','1')} booking bersamaan (batas keseluruhan).")
    name=input("Nama pelanggan: ").strip()
    if not name: print("Nama tidak boleh kosong."); return
    phone=input("Nomor telepon (opsional): ").strip()
    items=choose_services()
    if not items: return
    date=input("Tanggal (DD-MM-YYYY): ").strip()
    time=input("Jam (HH:MM): ").strip()
    try: start=datetime.strptime(date+" "+time,"%d-%m-%Y %H:%M")
    except ValueError: print("Format tanggal/jam tidak valid."); return
    if start <= datetime.now(): print("Tidak bisa booking pada waktu yang sudah lewat."); return
    ok,msg=db.check_availability(start,items)
    if not ok:
        print("\nJADWAL TIDAK TERSEDIA:",msg)
        suggestion=db.find_next_slot(start,items)
        if not suggestion:
            print("Tidak ada slot tersedia dalam 30 hari. Hubungi admin."); return
        print(f"Alternatif terdekat: {suggestion:%d-%m-%Y %H:%M}")
        if input("Gunakan jadwal alternatif? (yes/no): ").strip().lower()!="yes":
            print("Booking dibatalkan."); return
        start=suggestion
    duration=sum(x["duration_minutes"] for x in items)
    total=sum(x["price"] for x in items)
    end=start.replace() + __import__("datetime").timedelta(minutes=duration)
    print("\n========== BOOKING SUMMARY ==========")
    print("Customer:",name)
    print("Services:",", ".join(x["name"] for x in items))
    print("Start:",start.strftime("%d-%m-%Y %H:%M"))
    print("End:",end.strftime("%d-%m-%Y %H:%M"))
    print("Duration:",duration,"minutes")
    print("Total:",rupiah(total))
    if input("Konfirmasi booking? (yes/no): ").strip().lower()!="yes":
        print("Booking dibatalkan."); return
    try:
        bid=db.create_booking(name,phone,start,[x["id"] for x in items])
    except ValueError as exc:
        print("Booking belum tersimpan:",exc); return
    print(f"\nBooking #{bid} berhasil disimpan ke database.")
    try:
        event_id=sync_booking_to_google(bid)
        if event_id: print("Google Calendar: event berhasil dibuat.")
    except Exception as exc:
        print("Google Calendar belum tersinkron:",exc)
        print("Booking tetap aman tersimpan di database.")
    print("Ekspor kalender tersedia melalui menu admin.")

def admin_menu():
    while True:
        print("\n========== ADMIN MENU ==========")
        print("1. Atur kapasitas salon")
        print("2. Atur kapasitas per layanan")
        print("3. Lihat seluruh booking")
        print("4. Batalkan booking")
        print("5. Export kalender (.ics)")
        print("6. Export laporan Excel (.xlsx)")
        print("7. Kembali")
        choice=input("Pilih: ").strip()
        try:
            if choice=="1":
                n=int(input("Kapasitas salon bersamaan (minimal 1): "))
                if n<1: raise ValueError("Kapasitas minimal 1.")
                db.set_setting("salon_capacity",n)
                print("Kapasitas salon diperbarui.")
            elif choice=="2":
                rows=db.services()
                for s in rows: print(f"{s['id']}. {s['name']} (kapasitas {s['capacity']})")
                sid=int(input("ID layanan: "))
                cap=int(input("Kapasitas baru: "))
                db.update_service_capacity(sid,cap)
                print("Kapasitas layanan diperbarui.")
            elif choice=="3":
                rows=db.list_bookings()
                if not rows: print("Belum ada booking.")
                for b in rows:
                    print(f"#{b['id']} | {b['customer_name']} | {b['start_at']}–{b['end_at']} | {b['services']} | {b['status']} | {rupiah(b['total_price'])}")
            elif choice=="4":
                bid=int(input("ID booking yang dibatalkan: "))
                db.cancel_booking(bid)
                print("Booking dibatalkan.")
            elif choice=="5":
                path=export_ics()
                print("File kalender dibuat:",path)
            elif choice=="6":
                path=export_excel()
                print("Laporan Excel dibuat:",path)
            elif choice=="7": return
            else: print("Pilihan tidak dikenal.")
        except (ValueError,RuntimeError) as exc:
            print("Tidak dapat memproses:",exc)

def main():
    db.init_db()
    while True:
        print("\n================================")
        print("       GENIAL.AI")
        print("  Salon Booking Management")
        print("================================")
        print("1. Customer booking")
        print("2. Admin")
        print("3. Keluar")
        choice=input("Pilih menu: ").strip()
        if choice=="1": make_booking()
        elif choice=="2": admin_menu()
        elif choice=="3":
            print("Terima kasih telah menggunakan Genial.AI!")
            break
        else: print("Pilihan tidak valid.")

if __name__=="__main__":
    main()
