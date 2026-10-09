import os
import urllib.parse
from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from data_processor import DataStore
from export_docx import generate_docx
from export_pdf import generate_pdf

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
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
def startup_event():
    print("Iniciando DataStore...")
    DataStore.get_instance()
    print("DataStore inicializado correctamente.")

@app.get("/", response_class=HTMLResponse)
def get_index():
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Sistema de Ayuda Memoria País 2026 - PROMPERÚ</h1><p>Archivo templates/index.html no encontrado.</p>"

@app.get("/api/countries")
def get_countries():
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
    ds = DataStore.get_instance()
    report = ds.get_report(country_decoded)
    return report

@app.get("/api/export/docx")
def export_docx_endpoint(country: str = Query(..., description="Nombre del país")):
    country_decoded = urllib.parse.unquote(country).strip()
    if not country_decoded:
        raise HTTPException(status_code=400, detail="Debe especificar el país")
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
