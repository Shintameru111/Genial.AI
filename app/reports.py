from pathlib import Path
import database as db

ROOT=Path(__file__).resolve().parent.parent
EXPORT_DIR=ROOT/"data"/"exports"
EXPORT_DIR.mkdir(parents=True,exist_ok=True)

def export_excel(start_date=None,end_date=None):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter
    except ImportError as exc:
        raise RuntimeError("Jalankan: pip install -r requirements.txt") from exc

    rows=db.report_rows(start_date,end_date)
    wb=Workbook()
    ws=wb.active
    ws.title="Booking Report"
    ws.append(["Booking ID","Customer","Phone","Start","End","Services","Revenue (IDR)","Status"])
    for cell in ws[1]:
        cell.font=Font(bold=True,color="FFFFFF")
        cell.fill=PatternFill("solid",fgColor="285A8E")
        cell.alignment=Alignment(horizontal="center")
    for r in rows:
        ws.append([r["id"],r["customer_name"],r["phone"],r["start_at"],r["end_at"],
                   r["services"],r["total_price"],r["status"]])
    for col in ws.columns:
        width=max(len(str(c.value or "")) for c in col)+3
        ws.column_dimensions[get_column_letter(col[0].column)].width=min(width,42)
    ws.freeze_panes="A2"
    ws.auto_filter.ref=ws.dimensions
    path=EXPORT_DIR/"genial_booking_report.xlsx"
    wb.save(path)
    return path
