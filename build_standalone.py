import json
import os
import sys
from datetime import datetime
from data_processor import DataStore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "Ayuda_Memoria_País_PROMPERU_2026.html")

def build_standalone():
    print("Iniciando compilación de versión HTML autónoma y portable...")
    ds = DataStore.get_instance()
    
    # 1. Precomputar todos los reportes de los países
    print(f"Precomputando métricas para {len(ds.countries)} países...")
    all_reports = {}
    for item in ds.countries:
        c_name = item['name']
        rep = ds.get_report(c_name)
        all_reports[c_name] = rep

    countries_meta = ds.countries
    
    # Serializar a JSON
    reports_json_str = json.dumps(all_reports, ensure_ascii=False)
    countries_json_str = json.dumps(countries_meta, ensure_ascii=False)
    print(f"Base de datos serializada ({len(reports_json_str.encode('utf-8')) / 1024:.1f} KB).")

    # 2. Leer estilos CSS
    css_path = os.path.join(BASE_DIR, "static", "css", "styles.css")
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

    # 3. Construir el HTML completo
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PROMPERÚ — Ayuda Memoria País 2026 (Versión Autónoma Portable)</title>
  <meta name="description" content="Dashboard dinámico interactivo autónomo para análisis de exportaciones y generación de Ayuda Memoria País - PROMPERÚ.">
  
  <!-- Google Fonts: Inter & Outfit -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- FontAwesome 6 -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  
  <!-- Chart.js para visualización -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <style>
{css_content}

/* Ajustes específicos para versión autónoma */
.standalone-badge {{
  background: #EFF6FF;
  color: #1D4ED8;
  border: 1px solid #BFDBFE;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}}
  </style>
</head>
<body>

  <!-- Barra Superior Institucional -->
  <header class="navbar">
    <div class="nav-container">
      <div class="brand-group">
        <div class="brand-logo-mark">
          <span>PERÚ</span>
        </div>
        <div class="brand-text">
          <span class="brand-sub">PROMPERÚ • DPPM 2026</span>
          <h1 class="brand-title">Ayuda Memoria País — Ruta Exportadora</h1>
        </div>
      </div>
      
      <div class="nav-status">
        <span class="standalone-badge" title="Este archivo contiene todos los datos embebidos y funciona de forma autónoma en cualquier computadora sin internet ni servidor">
          <i class="fa-solid fa-laptop-file"></i>
          Versión Autónoma Portable (100% Funcional)
        </span>
      </div>
    </div>
  </header>

  <!-- Contenedor Principal -->
  <main class="main-container">

    <!-- Barra de Selección y Acciones -->
    <section class="control-panel card">
      <div class="control-grid">
        
        <!-- Selector con Búsqueda -->
        <div class="country-select-wrapper">
          <label for="countrySearchInput" class="control-label">
            <i class="fa-solid fa-earth-americas text-accent"></i> Seleccionar Mercado / País de Destino:
          </label>
          <div class="search-box-container">
            <i class="fa-solid fa-magnifying-glass search-icon"></i>
            <input 
              type="text" 
              id="countrySearchInput" 
              class="country-input" 
              placeholder="Buscar país (ej: Uruguay, China, Estados Unidos, España...)" 
              autocomplete="off"
            />
            <button id="clearSearchBtn" class="clear-btn" title="Limpiar búsqueda" style="display: none;">
              <i class="fa-solid fa-xmark"></i>
            </button>
            <div id="countriesDropdown" class="countries-dropdown" style="display: none;"></div>
          </div>
        </div>

        <!-- Botones de Descarga y Exportación -->
        <div class="action-buttons-group">
          <button id="downloadDocxBtn" class="btn btn-word" title="Descargar documento editable oficial en Word">
            <i class="fa-solid fa-file-word"></i>
            <span>Descargar en Word (.doc/.docx)</span>
          </button>
          
          <button id="downloadPdfBtn" class="btn btn-pdf" title="Guardar o imprimir reporte en PDF">
            <i class="fa-solid fa-file-pdf"></i>
            <span>Guardar en PDF</span>
          </button>
          
          <button id="copyReportBtn" class="btn btn-secondary" title="Copiar el texto oficial al portapapeles">
            <i class="fa-regular fa-copy"></i>
            <span>Copiar Texto</span>
          </button>

          <button id="printBtn" class="btn btn-outline" title="Imprimir documento">
            <i class="fa-solid fa-print"></i>
          </button>
        </div>

      </div>

      <!-- Accesos Rápidos (Chips) -->
      <div class="quick-chips-row">
        <span class="chips-label">Destinos Frecuentes:</span>
        <div class="chips-list" id="quickChipsContainer"></div>
      </div>
    </section>

    <!-- Contenido del Reporte -->
    <div id="reportContent" class="report-wrapper">

      <!-- Encabezado de País Activo -->
      <div class="country-header-banner">
        <div class="country-title-box">
          <div class="country-badge-icon">
            <i class="fa-solid fa-flag"></i>
          </div>
          <div>
            <h2 id="countryTitle" class="country-name">Uruguay</h2>
            <p id="countryMetaSubtitle" class="country-meta">Empresas exportadoras en Ruta Exportadora — Periodo 2024 / 2025 / 2026</p>
          </div>
        </div>
        <div class="header-tag">
          <span class="pulse-badge">Reporte Oficial Generado</span>
        </div>
      </div>

      <!-- Métricas Clave (KPI Cards) -->
      <section class="kpi-grid">
        
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Empresas Rutex</span>
            <div class="kpi-icon-wrap"><i class="fa-solid fa-building"></i></div>
          </div>
          <div class="kpi-body">
            <span id="kpiEmpresas" class="kpi-value">0</span>
          </div>
          <div class="kpi-footer">
            <span>Atendidas durante 2026</span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Partidas Únicas</span>
            <div class="kpi-icon-wrap"><i class="fa-solid fa-boxes-stacked"></i></div>
          </div>
          <div class="kpi-body">
            <span id="kpiPartidas" class="kpi-value">0</span>
          </div>
          <div class="kpi-footer">
            <span>Productos exportados 2025</span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Exportaciones 2025</span>
            <div class="kpi-icon-wrap"><i class="fa-solid fa-chart-line"></i></div>
          </div>
          <div class="kpi-body">
            <span id="kpiFob2025" class="kpi-value">USD 0.0M</span>
          </div>
          <div class="kpi-footer">
            <span id="kpiFob2025Exacto">FOB Total: $0</span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Exportaciones 2024</span>
            <div class="kpi-icon-wrap"><i class="fa-solid fa-calendar-days"></i></div>
          </div>
          <div class="kpi-body">
            <span id="kpiFob2024" class="kpi-value">USD 0.0M</span>
          </div>
          <div class="kpi-footer">
            <span id="kpiFob2024Exacto">FOB Total: $0</span>
          </div>
        </div>

        <div class="kpi-card" id="kpiVarCard">
          <div class="kpi-header">
            <span class="kpi-label">Variación Interanual</span>
            <div class="kpi-icon-wrap" id="kpiVarIcon"><i class="fa-solid fa-arrow-trend-up"></i></div>
          </div>
          <div class="kpi-body">
            <span id="kpiVarPct" class="kpi-value">0.00%</span>
          </div>
          <div class="kpi-footer">
            <span id="kpiVarTipo" class="var-badge">Variación respecto a 2024</span>
          </div>
        </div>

      </section>

      <!-- Panel de Dos Columnas: Vista Previa Oficial & Desgloses Top -->
      <div class="content-dual-grid">

        <!-- Columna 1: Vista Previa Oficial en Hoja de Estilo Memoria -->
        <section class="card paper-sheet-preview">
          <div class="paper-header-bar">
            <div class="paper-badge-official">
              <i class="fa-solid fa-shield-halved"></i>
              <span>VISTA PREVIA DE LA AYUDA MEMORIA OFICIAL</span>
            </div>
            <button id="copyPaperTextBtn" class="btn-copy-small" title="Copiar párrafos redactados">
              <i class="fa-regular fa-copy"></i> Copiar
            </button>
          </div>

          <div class="official-document-content" id="officialDocumentContent">
            <h2 class="doc-official-title" id="docTitle">Ayuda memoria</h2>
            <h3 class="doc-official-subtitle" id="docSubtitle">Empresas exportadoras a Uruguay - Ruta Exportadora</h3>
            
            <div class="doc-official-paragraphs">
              <p class="doc-paragraph" id="docP1"></p>
              <p class="doc-paragraph" id="docP2"></p>
              
              <div class="doc-events-section">
                <p class="doc-events-heading" id="docEventsHeading">
                  Los principales programas en donde participaron las empresas fueron:
                </p>
                <ul class="doc-events-bullets" id="docEventsBullets"></ul>
              </div>
            </div>
          </div>
        </section>

        <!-- Columna 2: Gráficos de Productos y Regiones Top 5 -->
        <div class="analytics-column">
          
          <!-- Top 5 Productos -->
          <section class="card">
            <div class="card-header-clean">
              <div class="header-icon-title">
                <i class="fa-solid fa-award text-accent"></i>
                <h3>Top 5 Productos Exportados (2025)</h3>
              </div>
              <span class="sub-badge">Cruce Rutex</span>
            </div>
            <div class="top-list-container" id="topProductsList"></div>
          </section>

          <!-- Top 5 Regiones -->
          <section class="card">
            <div class="card-header-clean">
              <div class="header-icon-title">
                <i class="fa-solid fa-map-location-dot text-accent"></i>
                <h3>Top 5 Regiones Exportadoras (2025)</h3>
              </div>
              <span class="sub-badge">Origen departamental</span>
            </div>
            <div class="top-list-container" id="topRegionsList"></div>
          </section>

        </div>

      </div>

      <!-- Sección: Histograma y Tabla de los 15 Eventos / Programas -->
      <section class="card events-section-card">
        <div class="events-card-header">
          <div>
            <h3 class="section-title">
              <i class="fa-solid fa-chart-column text-accent"></i>
              Programas y Eventos Ruta Exportadora con Mayor Participación (Top 15)
            </h3>
            <p class="section-subtitle">
              Distribución de empresas participantes atendidas en actividades y programas de capacitación
            </p>
          </div>
          
          <div class="view-toggle-tabs">
            <button class="tab-btn active" id="tabChartBtn">
              <i class="fa-solid fa-chart-bar"></i> Gráfico / Histograma
            </button>
            <button class="tab-btn" id="tabTableBtn">
              <i class="fa-solid fa-table-list"></i> Tabla Detallada
            </button>
          </div>
        </div>

        <!-- Vista de Gráfico -->
        <div id="chartView" class="view-panel active">
          <div class="chart-container-box">
            <canvas id="eventsBarChart"></canvas>
          </div>
        </div>

        <!-- Vista de Tabla -->
        <div id="tableView" class="view-panel" style="display: none;">
          <div class="table-responsive">
            <table class="promperu-table">
              <thead>
                <tr>
                  <th style="width: 60px; text-align: center;">#</th>
                  <th>Programa / Evento de Ruta Exportadora</th>
                  <th style="width: 220px; text-align: center;">Empresas Participantes</th>
                  <th style="width: 140px; text-align: center;">Participación</th>
                </tr>
              </thead>
              <tbody id="eventsTableBody"></tbody>
            </table>
          </div>
        </div>

      </section>

    </div>

  </main>

  <!-- Notificación Toast -->
  <div id="toastNotification" class="toast-box">
    <i class="fa-solid fa-check-circle toast-icon"></i>
    <span id="toastMessage">Texto copiado al portapapeles</span>
  </div>

  <!-- BASE DE DATOS PRECOMPUTADA EMBEBIDA -->
  <script>
    const EMBEDDED_COUNTRIES = {countries_json_str};
    const EMBEDDED_REPORTS = {reports_json_str};
  </script>

  <!-- LÓGICA AUTÓNOMA CLIENT-SIDE -->
  <script>
    const AppState = {{
      countries: EMBEDDED_COUNTRIES,
      reports: EMBEDDED_REPORTS,
      selectedCountry: 'Uruguay',
      currentReport: null,
      chartInstance: null
    }};

    const dom = {{
      searchInput: document.getElementById('countrySearchInput'),
      clearBtn: document.getElementById('clearSearchBtn'),
      dropdown: document.getElementById('countriesDropdown'),
      chipsContainer: document.getElementById('quickChipsContainer'),
      countryTitle: document.getElementById('countryTitle'),
      countryMetaSubtitle: document.getElementById('countryMetaSubtitle'),
      
      kpiEmpresas: document.getElementById('kpiEmpresas'),
      kpiPartidas: document.getElementById('kpiPartidas'),
      kpiFob2025: document.getElementById('kpiFob2025'),
      kpiFob2025Exacto: document.getElementById('kpiFob2025Exacto'),
      kpiFob2024: document.getElementById('kpiFob2024'),
      kpiFob2024Exacto: document.getElementById('kpiFob2024Exacto'),
      kpiVarCard: document.getElementById('kpiVarCard'),
      kpiVarPct: document.getElementById('kpiVarPct'),
      kpiVarTipo: document.getElementById('kpiVarTipo'),
      kpiVarIcon: document.getElementById('kpiVarIcon'),
      
      docTitle: document.getElementById('docTitle'),
      docSubtitle: document.getElementById('docSubtitle'),
      docP1: document.getElementById('docP1'),
      docP2: document.getElementById('docP2'),
      docEventsHeading: document.getElementById('docEventsHeading'),
      docEventsBullets: document.getElementById('docEventsBullets'),
      
      topProductsList: document.getElementById('topProductsList'),
      topRegionsList: document.getElementById('topRegionsList'),
      chartCanvas: document.getElementById('eventsBarChart'),
      eventsTableBody: document.getElementById('eventsTableBody'),
      tabChartBtn: document.getElementById('tabChartBtn'),
      tabTableBtn: document.getElementById('tabTableBtn'),
      chartView: document.getElementById('chartView'),
      tableView: document.getElementById('tableView'),
      
      downloadDocxBtn: document.getElementById('downloadDocxBtn'),
      downloadPdfBtn: document.getElementById('downloadPdfBtn'),
      copyReportBtn: document.getElementById('copyReportBtn'),
      copyPaperTextBtn: document.getElementById('copyPaperTextBtn'),
      printBtn: document.getElementById('printBtn'),
      toast: document.getElementById('toastNotification'),
      toastMessage: document.getElementById('toastMessage')
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      setupEventListeners();
      renderQuickChips();
      filterDropdown('');
      selectCountry('Uruguay');
    }});

    function setupEventListeners() {{
      dom.searchInput.addEventListener('input', handleSearchInput);
      dom.searchInput.addEventListener('focus', () => {{
        filterDropdown(dom.searchInput.value.trim());
        dom.dropdown.style.display = 'block';
      }});

      dom.clearBtn.addEventListener('click', () => {{
        dom.searchInput.value = '';
        dom.clearBtn.style.display = 'none';
        filterDropdown('');
        dom.searchInput.focus();
      }});

      document.addEventListener('click', (e) => {{
        if (!e.target.closest('.search-box-container')) {{
          dom.dropdown.style.display = 'none';
        }}
      }});

      dom.searchInput.addEventListener('keydown', handleKeyNavigation);

      dom.tabChartBtn.addEventListener('click', () => switchTab('chart'));
      dom.tabTableBtn.addEventListener('click', () => switchTab('table'));

      dom.downloadDocxBtn.addEventListener('click', downloadWordOfficial);
      dom.downloadPdfBtn.addEventListener('click', () => window.print());
      dom.copyReportBtn.addEventListener('click', copyFullReportText);
      dom.copyPaperTextBtn.addEventListener('click', copyFullReportText);
      dom.printBtn.addEventListener('click', () => window.print());
    }}

    function renderQuickChips() {{
      const frequentList = ['Uruguay', 'Estados Unidos', 'China', 'España', 'Países Bajos', 'Alemania', 'Chile', 'Colombia', 'México', 'Canadá', 'Brasil', 'Italia', 'Japón'];
      dom.chipsContainer.innerHTML = '';
      frequentList.forEach(cName => {{
        const exists = AppState.countries.find(c => c.name.toLowerCase() === cName.toLowerCase());
        if (exists) {{
          const chip = document.createElement('button');
          chip.className = `country-chip ${{cName.toLowerCase() === AppState.selectedCountry.toLowerCase() ? 'active' : ''}}`;
          chip.textContent = cName;
          chip.addEventListener('click', () => selectCountry(exists.name));
          dom.chipsContainer.appendChild(chip);
        }}
      }});
    }}

    function updateActiveChip() {{
      document.querySelectorAll('.country-chip').forEach(chip => {{
        if (chip.textContent.trim().toLowerCase() === AppState.selectedCountry.toLowerCase()) {{
          chip.classList.add('active');
        }} else {{
          chip.classList.remove('active');
        }}
      }});
    }}

    function filterDropdown(query) {{
      const q = query.toLowerCase();
      const filtered = AppState.countries.filter(c => c.name.toLowerCase().includes(q));
      dom.dropdown.innerHTML = '';

      if (filtered.length === 0) {{
        const emptyItem = document.createElement('div');
        emptyItem.className = 'dropdown-item';
        emptyItem.style.color = '#9CA3AF';
        emptyItem.textContent = 'No se encontraron países con ese nombre';
        dom.dropdown.appendChild(emptyItem);
        return;
      }}

      filtered.forEach(c => {{
        const item = document.createElement('div');
        item.className = `dropdown-item ${{c.name.toLowerCase() === AppState.selectedCountry.toLowerCase() ? 'active' : ''}}`;
        const fobTxt = c.fob_2025 > 0 ? (c.fob_2025 >= 1e6 ? `$${{(c.fob_2025/1e6).toFixed(1)}}M` : `$${{(c.fob_2025/1e3).toFixed(0)}}k`) : '$0';
        item.innerHTML = `
          <span class="dropdown-item-name">${{c.name}}</span>
          <div class="dropdown-item-badges">
            ${{c.rutex_companies > 0 ? `<span class="badge-rutex-sm">${{c.rutex_companies}} emp.</span>` : ''}}
            ${{c.fob_2025 > 0 ? `<span class="badge-fob-sm">${{fobTxt}}</span>` : ''}}
          </div>
        `;
        item.addEventListener('click', () => {{
          selectCountry(c.name);
          dom.dropdown.style.display = 'none';
        }});
        dom.dropdown.appendChild(item);
      }});
    }}

    function handleSearchInput(e) {{
      const query = e.target.value;
      dom.clearBtn.style.display = query ? 'flex' : 'none';
      filterDropdown(query.trim());
      dom.dropdown.style.display = 'block';
    }}

    function handleKeyNavigation(e) {{
      const items = dom.dropdown.querySelectorAll('.dropdown-item:not([style*="color"])');
      if (!items.length) return;

      let activeIndex = -1;
      items.forEach((item, idx) => {{
        if (item.classList.contains('active')) activeIndex = idx;
      }});

      if (e.key === 'ArrowDown') {{
        e.preventDefault();
        dom.dropdown.style.display = 'block';
        const nextIndex = activeIndex < items.length - 1 ? activeIndex + 1 : 0;
        highlightDropdownItem(items, nextIndex);
      }} else if (e.key === 'ArrowUp') {{
        e.preventDefault();
        dom.dropdown.style.display = 'block';
        const prevIndex = activeIndex > 0 ? activeIndex - 1 : items.length - 1;
        highlightDropdownItem(items, prevIndex);
      }} else if (e.key === 'Enter') {{
        e.preventDefault();
        if (activeIndex >= 0 && items[activeIndex]) {{
          items[activeIndex].click();
        }}
      }} else if (e.key === 'Escape') {{
        dom.dropdown.style.display = 'none';
      }}
    }}

    function highlightDropdownItem(items, index) {{
      items.forEach(it => it.classList.remove('active'));
      const current = items[index];
      if (current) {{
        current.classList.add('active');
        current.scrollIntoView({{ block: 'nearest' }});
      }}
    }}

    function selectCountry(countryName) {{
      if (!countryName) return;
      const report = AppState.reports[countryName];
      if (!report) return;

      AppState.selectedCountry = countryName;
      AppState.currentReport = report;
      dom.searchInput.value = countryName;
      dom.clearBtn.style.display = 'flex';
      dom.dropdown.style.display = 'none';
      updateActiveChip();

      renderReport(report);
    }}

    function renderReport(report) {{
      const m = report.metrics;
      const p = report.paragraphs;

      dom.countryTitle.textContent = report.country_display || report.country;
      dom.countryMetaSubtitle.textContent = `Empresas exportadoras en Ruta Exportadora — Periodo 2024 / 2025 / 2026`;

      dom.kpiEmpresas.textContent = m.cant_empresas_rutex.toLocaleString('es-PE');
      dom.kpiPartidas.textContent = m.cant_productos_rutex.toLocaleString('es-PE');
      dom.kpiFob2025.textContent = `USD ${{m.fob_2025_millones.toFixed(1)}}M`;
      dom.kpiFob2025Exacto.textContent = `FOB Total: US$ ${{m.fob_2025_total.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }})}}`;
      dom.kpiFob2024.textContent = `USD ${{m.fob_2024_millones.toFixed(1)}}M`;
      dom.kpiFob2024Exacto.textContent = `FOB Total: US$ ${{m.fob_2024_total.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }})}}`;

      const varSign = m.is_positive ? '+' : '';
      dom.kpiVarPct.textContent = `${{varSign}}${{m.var_pct.toFixed(2)}}%`;

      if (m.is_positive) {{
        dom.kpiVarTipo.textContent = 'Incremento interanual';
        dom.kpiVarTipo.className = 'var-badge var-positive';
        dom.kpiVarIcon.innerHTML = '<i class="fa-solid fa-arrow-trend-up text-accent" style="color: #16A34A;"></i>';
      }} else {{
        dom.kpiVarTipo.textContent = 'Disminución interanual';
        dom.kpiVarTipo.className = 'var-badge var-negative';
        dom.kpiVarIcon.innerHTML = '<i class="fa-solid fa-arrow-trend-down text-accent" style="color: #DC2626;"></i>';
      }}

      dom.docTitle.textContent = report.title;
      dom.docSubtitle.textContent = report.subtitle;
      dom.docP1.textContent = p.p1;
      dom.docP2.textContent = p.p2;
      dom.docEventsHeading.textContent = p.events_heading;

      dom.docEventsBullets.innerHTML = '';
      if (p.events_bullets && p.events_bullets.length > 0) {{
        p.events_bullets.forEach(txt => {{
          const li = document.createElement('li');
          li.textContent = txt;
          dom.docEventsBullets.appendChild(li);
        }});
      }} else {{
        const li = document.createElement('li');
        li.textContent = "No se registraron eventos o programas para las empresas exportadoras a este destino.";
        dom.docEventsBullets.appendChild(li);
      }}

      renderTopProducts(report.top_productos);
      renderTopRegions(report.top_regiones);
      renderEventsChart(report.top_eventos);
      renderEventsTable(report.top_eventos);
    }}

    function renderTopProducts(products) {{
      dom.topProductsList.innerHTML = '';
      if (!products || products.length === 0) {{
        dom.topProductsList.innerHTML = '<p style="color: #9CA3AF; font-size: 0.85rem;">Sin registros de productos para este mercado.</p>';
        return;
      }}
      products.forEach(p => {{
        const row = document.createElement('div');
        row.className = 'top-item-row';
        row.innerHTML = `
          <div class="top-item-meta">
            <span class="top-item-title" title="${{p.partida}}">${{p.descripcion_limpia}}</span>
            <span class="top-item-val">${{p.fob_formatted}} (${{p.share_pct}}%)</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${{Math.min(100, Math.max(5, p.share_pct))}}%;"></div>
          </div>
        `;
        dom.topProductsList.appendChild(row);
      }});
    }}

    function renderTopRegions(regions) {{
      dom.topRegionsList.innerHTML = '';
      if (!regions || regions.length === 0) {{
        dom.topRegionsList.innerHTML = '<p style="color: #9CA3AF; font-size: 0.85rem;">Sin registros regionales para este mercado.</p>';
        return;
      }}
      regions.forEach(r => {{
        const row = document.createElement('div');
        row.className = 'top-item-row';
        const empWord = r.empresas === 1 ? 'empresa' : 'empresas';
        row.innerHTML = `
          <div class="top-item-meta">
            <span class="top-item-title"><strong>${{r.region}}</strong> (${{r.empresas}} ${{empWord}})</span>
            <span class="top-item-val">${{r.fob_formatted}} (${{r.share_pct}}%)</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${{Math.min(100, Math.max(5, r.share_pct))}}%; background: #003366;"></div>
          </div>
        `;
        dom.topRegionsList.appendChild(row);
      }});
    }}

    function renderEventsChart(events) {{
      if (AppState.chartInstance) {{
        AppState.chartInstance.destroy();
      }}
      if (!events || events.length === 0) return;

      const labels = events.map(e => e.evento.length > 55 ? e.evento.substring(0, 52) + '...' : e.evento);
      const data = events.map(e => e.empresas);
      const ctx = dom.chartCanvas.getContext('2d');

      const gradient = ctx.createLinearGradient(0, 0, 400, 0);
      gradient.addColorStop(0, '#D12628');
      gradient.addColorStop(1, '#E65100');

      AppState.chartInstance = new Chart(ctx, {{
        type: 'bar',
        data: {{
          labels: labels,
          datasets: [{{
            label: 'Empresas Participantes',
            data: data,
            backgroundColor: gradient,
            borderRadius: 6,
            barPercentage: 0.72,
            categoryPercentage: 0.85
          }}]
        }},
        options: {{
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              backgroundColor: '#111827',
              callbacks: {{
                title: function(items) {{ return events[items[0].dataIndex].evento; }},
                label: function(ctx) {{ return `${{ctx.raw}} ${{ctx.raw === 1 ? 'empresa participante' : 'empresas participantes'}}`; }}
              }}
            }}
          }},
          scales: {{
            x: {{ beginAtZero: true, ticks: {{ precision: 0 }} }},
            y: {{ ticks: {{ font: {{ size: 11 }} }} }}
          }}
        }}
      }});
    }}

    function renderEventsTable(events) {{
      dom.eventsTableBody.innerHTML = '';
      if (!events || events.length === 0) {{
        dom.eventsTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #9CA3AF; padding: 2rem;">No se registraron eventos.</td></tr>';
        return;
      }}
      const maxVal = Math.max(...events.map(e => e.empresas), 1);
      events.forEach(ev => {{
        const tr = document.createElement('tr');
        let rankClass = ev.rank === 1 ? 'rank-1' : (ev.rank === 2 ? 'rank-2' : (ev.rank === 3 ? 'rank-3' : ''));
        const pct = Math.round((ev.empresas / maxVal) * 100);
        tr.innerHTML = `
          <td style="text-align: center;"><span class="rank-badge ${{rankClass}}">${{ev.rank}}</span></td>
          <td><strong>${{ev.evento}}</strong></td>
          <td style="text-align: center;"><span class="badge-count">${{ev.empresas}} ${{ev.empresas === 1 ? 'empresa' : 'empresas'}}</span></td>
          <td style="text-align: center;">
            <div class="progress-track" style="margin: 0 auto; width: 100px;">
              <div class="progress-fill" style="width: ${{pct}}%;"></div>
            </div>
          </td>
        `;
        dom.eventsTableBody.appendChild(tr);
      }});
    }}

    function switchTab(target) {{
      if (target === 'chart') {{
        dom.tabChartBtn.classList.add('active');
        dom.tabTableBtn.classList.remove('active');
        dom.chartView.style.display = 'block';
        dom.tableView.style.display = 'none';
      }} else {{
        dom.tabTableBtn.classList.add('active');
        dom.tabChartBtn.classList.remove('active');
        dom.chartView.style.display = 'none';
        dom.tableView.style.display = 'block';
      }}
    }}

    // EXPORTACIÓN WORD CLIENT-SIDE TOTALMENTE AUTÓNOMA
    function downloadWordOfficial() {{
      if (!AppState.currentReport) return;
      const r = AppState.currentReport;
      const p = r.paragraphs;

      let bulletsHtml = '';
      if (p.events_bullets && p.events_bullets.length > 0) {{
        p.events_bullets.forEach(b => {{
          bulletsHtml += `<li style="font-family: Calibri, sans-serif; font-size: 11pt; margin-bottom: 3pt; line-height: 1.15;">${{b}}</li>`;
        }});
      }} else {{
        bulletsHtml = '<li style="font-family: Calibri, sans-serif; font-size: 11pt;">No se registraron eventos o programas para las empresas exportadoras a este destino.</li>';
      }}

      const wordDocContent = `
        <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
        <head>
          <meta charset='utf-8'>
          <title>${{r.title}}</title>
          <style>
            @page {{
              size: 8.5in 11.0in;
              margin: 1.0in;
            }}
            body {{
              font-family: 'Calibri', sans-serif;
              font-size: 11pt;
              line-height: 1.15;
              color: #000000;
            }}
            h1.title {{
              font-family: 'Calibri', sans-serif;
              font-size: 20pt;
              font-weight: bold;
              color: #003366;
              margin-top: 0;
              margin-bottom: 4pt;
            }}
            h2.subtitle {{
              font-family: 'Calibri', sans-serif;
              font-size: 14pt;
              font-weight: bold;
              color: #505050;
              margin-top: 0;
              margin-bottom: 14pt;
            }}
            p.body-p {{
              font-family: 'Calibri', sans-serif;
              font-size: 11pt;
              line-height: 1.15;
              margin-bottom: 8pt;
              text-align: justify;
            }}
            p.events-h {{
              font-family: 'Calibri', sans-serif;
              font-size: 11pt;
              font-weight: bold;
              margin-top: 10pt;
              margin-bottom: 6pt;
            }}
            ul.events-l {{
              margin-top: 0;
              margin-bottom: 12pt;
              padding-left: 20pt;
            }}
          </style>
        </head>
        <body>
          <h1 class="title">${{r.title}}</h1>
          <h2 class="subtitle">${{r.subtitle}}</h2>
          <p class="body-p">${{p.p1}}</p>
          <p class="body-p">${{p.p2}}</p>
          <p class="events-h">${{p.events_heading}}</p>
          <ul class="events-l">
            ${{bulletsHtml}}
          </ul>
        </body>
        </html>
      `;

      const blob = new Blob(['\\ufeff', wordDocContent], {{ type: 'application/msword' }});
      const filename = `Ayuda_Memoria_Exportaciones_${{r.country.replace(/ /g, '_')}}.doc`;
      
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);

      showToast('Documento Word descargado exitosamente');
    }}

    function copyFullReportText() {{
      if (!AppState.currentReport) return;
      const r = AppState.currentReport;
      const p = r.paragraphs;

      let textToCopy = `${{r.title}}\\n${{r.subtitle}}\\n\\n${{p.p1}}\\n\\n${{p.p2}}\\n\\n${{p.events_heading}}\\n`;
      if (p.events_bullets && p.events_bullets.length > 0) {{
        p.events_bullets.forEach(b => {{ textToCopy += `• ${{b}}\\n`; }});
      }}

      navigator.clipboard.writeText(textToCopy).then(() => {{
        showToast('¡Texto oficial copiado al portapapeles!');
      }}).catch(() => {{
        showToast('No se pudo copiar automáticamente', true);
      }});
    }}

    function showToast(msg, isError = false) {{
      dom.toastMessage.textContent = msg;
      dom.toast.querySelector('.toast-icon').className = isError 
        ? 'fa-solid fa-circle-exclamation toast-icon' 
        : 'fa-solid fa-check-circle toast-icon';
      dom.toast.querySelector('.toast-icon').style.color = isError ? '#DC2626' : '#16A34A';
      dom.toast.classList.add('show');
      setTimeout(() => {{ dom.toast.classList.remove('show'); }}, 3200);
    }}
  </script>
</body>
</html>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    index_file = os.path.join(BASE_DIR, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] Archivo HTML autonomo generado exitosamente: {OUTPUT_FILE}")
    print(f"[OK] Archivo index.html generado exitosamente: {index_file}")
    print(f"Tamano final del archivo: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")

if __name__ == "__main__":
    build_standalone()
