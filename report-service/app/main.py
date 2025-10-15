from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, Response
import httpx
from typing import Optional, List, Dict, Any
from io import BytesIO
import os

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


import os
FINANCE_SERVICE_URL = os.getenv("FINANCE_SERVICE_URL", "http://localhost:8001")

app = FastAPI(
    title="Report Service",
    description="Легкий сервис отчетности (summary, CSV export)",
    version="1.0.0"
)


CYR_FONT_NAME = "_CyrillicFont"

def try_register_cyrillic_font() -> bool:
    if not REPORTLAB_AVAILABLE:
        return False
    # Common font paths for Windows/macOS/Linux
    candidate_paths = [
        # Windows
        r"C:\\Windows\\Fonts\\arial.ttf",
        r"C:\\Windows\\Fonts\\segoeui.ttf",
        r"C:\\Windows\\Fonts\\tahoma.ttf",
        # macOS
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        # Linux (DejaVu)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for path in candidate_paths:
        try:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont(CYR_FONT_NAME, path))
                return True
        except Exception:
            continue
    return False


@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        response = JSONResponse(content={"message": "CORS preflight"})
    else:
        response = await call_next(request)

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.options("/{path:path}")
async def options_handler(path: str):
    return JSONResponse(
        content={"message": "CORS preflight"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Allow-Credentials": "true",
        },
    )


async def fetch_operations(authorization: Optional[str], branch_id: Optional[int]) -> List[Dict[str, Any]]:
    params = {}
    if branch_id is not None:
        params["branch_id"] = branch_id
    headers = {}
    if authorization:
        headers["Authorization"] = authorization
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{FINANCE_SERVICE_URL}/operations", params=params, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()


def compute_summary(operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_income = 0.0
    total_expense = 0.0
    by_branch: Dict[int, Dict[str, float]] = {}

    for op in operations:
        amount = float(op.get("amount", 0) or 0)
        branch = int(op.get("branch_id", 0) or 0)
        kind = op.get("type", "")

        if branch not in by_branch:
            by_branch[branch] = {"income": 0.0, "expense": 0.0}

        if kind == "income":
            total_income += amount
            by_branch[branch]["income"] += amount
        elif kind == "expense":
            total_expense += amount
            by_branch[branch]["expense"] += amount

    total_balance = total_income - total_expense
    branches = [
        {
            "branch_id": b,
            "income": round(vals["income"], 2),
            "expense": round(vals["expense"], 2),
            "balance": round(vals["income"] - vals["expense"], 2),
        }
        for b, vals in sorted(by_branch.items(), key=lambda x: x[0])
    ]

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "total_balance": round(total_balance, 2),
        "branches": branches,
        "count": len(operations),
    }


@app.get("/summary")
async def summary(request: Request, branch_id: Optional[int] = None, limit: Optional[int] = 10):
    authorization = request.headers.get("Authorization")
    operations = await fetch_operations(authorization, branch_id)
    data = compute_summary(operations)
    try:
        ops_sorted = sorted(operations, key=lambda o: o.get("created_at", ""))
        if limit is not None:
            ops_sorted = ops_sorted[-int(limit):]
    except Exception:
        ops_sorted = operations
    data["recent"] = ops_sorted
    return data


@app.get("/export.csv")
async def export_csv(request: Request, branch_id: Optional[int] = None, limit: Optional[int] = None):
    authorization = request.headers.get("Authorization")
    operations = await fetch_operations(authorization, branch_id)
    if limit is not None:
        try:
            operations = sorted(operations, key=lambda o: o.get("created_at", ""))[-int(limit):]
        except Exception:
            pass

    # CSV header
    rows = ["id,type,amount,description,branch_id,created_at"]
    for op in operations:
        # минимальная экранизация запятых
        description = str(op.get("description", "")).replace(",", " ")
        row = f"{op.get('id','')},{op.get('type','')},{op.get('amount','')},{description},{op.get('branch_id','')},{op.get('created_at','')}"
        rows.append(row)
    csv_data = "\n".join(rows)

    return PlainTextResponse(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=operations_export.csv"},
    )


@app.get("/export.pdf")
async def export_pdf(request: Request, branch_id: Optional[int] = None, limit: Optional[int] = 20):
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF engine not available. Install reportlab.")

    authorization = request.headers.get("Authorization")
    operations = await fetch_operations(authorization, branch_id)
    summary = compute_summary(operations)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Ensure Cyrillic font is registered
    font_ok = try_register_cyrillic_font()
    title_font = CYR_FONT_NAME if font_ok else "Helvetica-Bold"
    text_font = CYR_FONT_NAME if font_ok else "Helvetica"

    # Header
    c.setFont(title_font, 16)
    c.drawString(25 * mm, height - 25 * mm, "Отчет по операциям")
    c.setFont(text_font, 10)
    c.drawString(25 * mm, height - 32 * mm, f"Всего операций: {summary['count']}")
    c.drawString(25 * mm, height - 37 * mm, f"Доход: {summary['total_income']} | Расход: {summary['total_expense']} | Баланс: {summary['total_balance']}")

    # Branch table
    y = height - 50 * mm
    c.setFont(title_font, 12)
    c.drawString(25 * mm, y, "Филиалы:")
    y -= 8 * mm
    c.setFont(text_font, 10)
    c.drawString(25 * mm, y, "Филиал")
    c.drawString(60 * mm, y, "Доход")
    c.drawString(95 * mm, y, "Расход")
    c.drawString(130 * mm, y, "Баланс")
    y -= 6 * mm
    for b in summary['branches']:
        c.drawString(25 * mm, y, str(b['branch_id']))
        c.drawRightString(88 * mm, y, f"{b['income']}")
        c.drawRightString(123 * mm, y, f"{b['expense']}")
        c.drawRightString(158 * mm, y, f"{b['balance']}")
        y -= 6 * mm
        if y < 25 * mm:
            c.showPage()
            y = height - 25 * mm

    # Recent operations table
    try:
        ops_sorted = sorted(operations, key=lambda o: o.get("created_at", ""))
        if limit is not None:
            ops_sorted = ops_sorted[-int(limit):]
    except Exception:
        ops_sorted = operations

    y -= 10 * mm
    if y < 40 * mm:
        c.showPage(); y = height - 25 * mm
    c.setFont(title_font, 12)
    c.drawString(25 * mm, y, "История операций:")
    y -= 8 * mm
    c.setFont(text_font, 9)
    # headers
    c.drawString(25 * mm, y, "Дата")
    c.drawString(55 * mm, y, "Тип")
    c.drawString(75 * mm, y, "Сумма")
    c.drawString(100 * mm, y, "Описание")
    c.drawString(165 * mm, y, "Филиал")
    y -= 6 * mm
    for op in ops_sorted:
        date_str = str(op.get("created_at", ""))[:19]
        typ = str(op.get("type", ""))
        amount = str(op.get("amount", ""))
        desc = str(op.get("description", ""))
        if len(desc) > 60:
            desc = desc[:57] + "..."
        branch = str(op.get("branch_id", ""))

        c.drawString(25 * mm, y, date_str)
        c.drawString(55 * mm, y, typ)
        c.drawRightString(95 * mm, y, amount)
        c.drawString(100 * mm, y, desc)
        c.drawRightString(185 * mm, y, branch)
        y -= 6 * mm
        if y < 25 * mm:
            c.showPage()
            y = height - 25 * mm
            c.setFont(text_font, 9)

    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=report.pdf"})


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "report-service"}


if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск Report Service...")
    uvicorn.run(app, host="0.0.0.0", port=8002)


