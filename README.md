# PROMPERÚ — Sistema de Ayuda Memoria País 2026

Aplicación web y dashboard interactivo de alto rendimiento para el análisis centralizado de exportaciones peruanas y la generación automatizada de la **Ayuda Memoria por País**, con respaldo institucional para **Ruta Exportadora (RUTEX)** y la Dirección de Promoción de las Exportaciones (**DPPM 2026**).

---

## 🌟 Características Principales

1. **Procesamiento de Datos Automatizado y de Alta Velocidad**:
   - Cruce exacto por **RUC** estandarizado entre las bases de datos `EXPORTACIONES 2024.xlsx`, `EXPORTACIONES 2025.xlsx` y `base rutex 29.09.2026 - Colab.xlsx`.
   - Cálculo en tiempo real de:
     - Número de empresas exportadoras en Ruta Exportadora atendidas en 2026.
     - Número de partidas arancelarias únicas (productos) exportados en 2025.
     - Total FOB USD 2024 y 2025 (y variación porcentual interanual con calificación de *incremento* o *disminución*).
     - **Top 5 Productos** con descripción limpia, importe FOB y participación.
     - **Top 5 Regiones / Departamentos** con número de empresas y monto FOB.
     - **Top 15 Programas / Eventos** de Ruta Exportadora con mayor cantidad de empresas participantes.
   - Sistema de caché optimizado con carga en memoria en **0.06 segundos**.

2. **Interfaz de Usuario (UI/UX) Moderna e Institucional**:
   - Paleta de colores oficial de **PROMPERÚ** (`#D12628` rojo institucional, `#003366` azul de títulos oficiales, fondos limpios `#F4F6F9`, tipografías Inter y Outfit).
   - Selector interactivo con **búsqueda predictiva instantánea** y navegación por teclado.
   - Accesos directos rápidos (chips) a mercados frecuentes (Uruguay, EE.UU., China, España, etc.).
   - Tarjetas KPI interactivas con badges dinámicos de crecimiento o decrecimiento.
   - Vista Previa Oficial tipo hoja de papel que replica exactamente la diagramación de la plantilla oficial.

3. **Data Visualization**:
   - **Histograma / Gráfico de Barras Horizontal Interactivo** (Chart.js) de los 15 eventos con gradiente institucional y tooltips detallados.
   - **Vista de Tabla Detallada** con medallas de ranking (#1, #2, #3) y barras de proporción.
   - Barras de progreso de participación en los Top 5 productos y regiones.

4. **Exportación y Descargas Oficiales**:
   - **Descargar en Word (.docx)**: Genera el archivo oficial editable (`.docx`) respetando fielmente la estructura, estilos Calibri, títulos en azul institucional y viñetas idénticas a `Ayuda_Memoria_Exportaciones_Uruguay.docx`.
   - **Descargar en PDF (.pdf)**: Genera un reporte ejecutivo en PDF mediante ReportLab con membrete institucional PROMPERÚ, tabla de KPIs, redacción ejecutiva y tabla diagramada de los 15 programas.
   - **Copiar Texto**: Copia en un solo clic la redacción oficial directamente al portapapeles.
   - **Impresión Directa**: Optimizado con reglas CSS `@media print`.

---

## 🚀 Cómo Ejecutar la Aplicación

### Opción 1: Visualización Web Inmediata / GitHub Pages
El proyecto incluye `index.html` (y `Ayuda_Memoria_País_PROMPERU_2026.html`), una versión cliente **100% autónoma, interactiva y responsive**.

- **En línea vía GitHub Pages**: [https://dannygambini-project.github.io/Ayuda-Memoria-Pais-Ruta-Exportadora/](https://dannygambini-project.github.io/Ayuda-Memoria-Pais-Ruta-Exportadora/)
- **Localmente**: Simplemente abre `index.html` haciendo doble clic en cualquier navegador (Chrome, Edge, Firefox, Safari).

Contiene **toda la base de datos precomputada de los 186 países de destino** con:
- Búsqueda predictiva con autocompletado y accesos rápidos (chips).
- 5 Tarjetas KPI actualizadas dinámicamente con valores exactos en USD FOB.
- Visualización de datos interactiva con **Chart.js** (histograma horizontal y tabla clasificada).
- Desglose de Top 5 Productos y Top 5 Regiones exportadoras.
- Generador y descarga de documento oficial en Word (.doc/.docx), copia al portapapeles e impresión.

Si actualizas las bases de datos de Excel en el futuro, puedes regenerar `index.html` ejecutando:
```bash
python build_standalone.py
```

---

### Opción 2: Servidor Local Interactivo (FastAPI)
Con doble clic sobre el archivo:
```bat
run_app.bat
```
O desde la terminal:
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
Abre tu navegador en: **http://127.0.0.1:8000**

---

## 📁 Estructura del Proyecto

```text
├── app.py                     # Servidor FastAPI con rutas REST y vistas HTML
├── data_processor.py          # Motor de procesamiento, cruce RUC, estadísticas y caché
├── export_docx.py             # Generador del documento Word (.docx) oficial
├── export_pdf.py              # Generador del informe PDF institucional con ReportLab
├── requirements.txt           # Dependencias del proyecto
├── run_app.bat                # Script de inicio rápido en Windows
├── templates/
│   └── index.html             # Interfaz web moderna con componentes PROMPERÚ
├── static/
│   ├── css/
│   │   └── styles.css         # Hoja de estilos con paleta y tokens institucionales
│   └── js/
│       └── app.js             # Lógica frontend, autocompletado y gráficos interactivos
└── .cache/                    # Caché binaria ultra-rápida autogenerada
```

---

## 🛠️ Tecnologías Empleadas

- **Backend**: Python 3, FastAPI, Uvicorn, Pandas, OpenpyXL, Python-docx, ReportLab.
- **Frontend**: HTML5 Semántico, Vanilla CSS (Design System PROMPERÚ), JavaScript (ES6+), Chart.js, FontAwesome 6, Google Fonts.
- **Data Engineering**: Optimización de cruces relacionales por RUC y serialización optimizada para consultas en < 30ms.
