import os
import urllib.parse
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PROMPERÚ - Ayuda Memoria País 2026",
    description="API y Dashboard interactivo para la generación automatizada de la Ayuda Memoria por País",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
def get_index():
    # 1. Prioridad: Versión autónoma compilada index.html con todos los 186 países embebidos
    root_index = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(root_index):
        with open(root_index, "r", encoding="utf-8") as f:
            return f.read()
    
    # 2. Alternativa: Plantilla en templates/index.html
    template_index = os.path.join(BASE_DIR, "templates", "index.html")
    if os.path.exists(template_index):
        with open(template_index, "r", encoding="utf-8") as f:
            return f.read()
            
    return "<h1>Sistema de Ayuda Memoria País 2026 - PROMPERÚ</h1><p>Archivo index.html no encontrado.</p>"

@app.get("/api/countries")
def get_countries():
    from data_processor import DataStore
    ds = DataStore.get_instance()
    return {
        "total": len(ds.countries),
        "countries": ds.countries
    }

@app.get("/api/report")
def get_report(country: str = Query(..., description="Nombre del país a consultar")):
    country_decoded = urllib.parse.unquote(country).strip()
    if not country_decoded:
        raise HTTPException(status_code=400, detail="Debe especificar el país")
    from data_processor import DataStore
    ds = DataStore.get_instance()
    report = ds.get_report(country_decoded)
    return report

@app.get("/api/export/docx")
def export_docx_endpoint(country: str = Query(..., description="Nombre del país")):
    country_decoded = urllib.parse.unquote(country).strip()
    if not country_decoded:
        raise HTTPException(status_code=400, detail="Debe especificar el país")
    from data_processor import DataStore
    from export_docx import generate_docx
    ds = DataStore.get_instance()
    report = ds.get_report(country_decoded)
    buffer = generate_docx(report)
    
    clean_country = country_decoded.replace(' ', '_')
    filename = f"Ayuda_Memoria_Exportaciones_{clean_country}.docx"
    
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Access-Control-Expose-Headers": "Content-Disposition"
    }
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers
    )

@app.get("/api/export/pdf")
def export_pdf_endpoint(country: str = Query(..., description="Nombre del país")):
    country_decoded = urllib.parse.unquote(country).strip()
    if not country_decoded:
        raise HTTPException(status_code=400, detail="Debe especificar el país")
    from data_processor import DataStore
    from export_pdf import generate_pdf
    ds = DataStore.get_instance()
    report = ds.get_report(country_decoded)
    buffer = generate_pdf(report)
    
    clean_country = country_decoded.replace(' ', '_')
    filename = f"Ayuda_Memoria_Exportaciones_{clean_country}.pdf"
    
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Access-Control-Expose-Headers": "Content-Disposition"
    }
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers=headers
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
