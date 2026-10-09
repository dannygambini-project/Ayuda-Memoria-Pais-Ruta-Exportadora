/**
 * PROMPERÚ — Sistema de Ayuda Memoria País 2026
 * Frontend Logic & Data Visualization
 */

// Estado global de la aplicación
const AppState = {
  countries: [],
  selectedCountry: 'Uruguay',
  currentReport: null,
  chartInstance: null,
};

// Elementos DOM
const dom = {
  searchInput: document.getElementById('countrySearchInput'),
  clearBtn: document.getElementById('clearSearchBtn'),
  dropdown: document.getElementById('countriesDropdown'),
  chipsContainer: document.getElementById('quickChipsContainer'),
  loadingOverlay: document.getElementById('loadingOverlay'),
  reportContent: document.getElementById('reportContent'),
  
  // Banner de País
  countryTitle: document.getElementById('countryTitle'),
  countryMetaSubtitle: document.getElementById('countryMetaSubtitle'),
  
  // KPIs
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
  
  // Documento Oficial
  docTitle: document.getElementById('docTitle'),
  docSubtitle: document.getElementById('docSubtitle'),
  docP1: document.getElementById('docP1'),
  docP2: document.getElementById('docP2'),
  docEventsHeading: document.getElementById('docEventsHeading'),
  docEventsBullets: document.getElementById('docEventsBullets'),
  
  // Top Lists
  topProductsList: document.getElementById('topProductsList'),
  topRegionsList: document.getElementById('topRegionsList'),
  
  // Eventos
  chartCanvas: document.getElementById('eventsBarChart'),
  eventsTableBody: document.getElementById('eventsTableBody'),
  tabChartBtn: document.getElementById('tabChartBtn'),
  tabTableBtn: document.getElementById('tabTableBtn'),
  chartView: document.getElementById('chartView'),
  tableView: document.getElementById('tableView'),
  
  // Botones de acción
  downloadDocxBtn: document.getElementById('downloadDocxBtn'),
  downloadPdfBtn: document.getElementById('downloadPdfBtn'),
  copyReportBtn: document.getElementById('copyReportBtn'),
  copyPaperTextBtn: document.getElementById('copyPaperTextBtn'),
  printBtn: document.getElementById('printBtn'),
  
  // Toast
  toast: document.getElementById('toastNotification'),
  toastMessage: document.getElementById('toastMessage')
};

// ============================================================
// INICIALIZACIÓN
// ============================================================
document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  await loadCountries();
  // Cargar Uruguay por defecto como en el ejemplo oficial
  await selectCountry('Uruguay');
});

function setupEventListeners() {
  // Búsqueda en Input
  dom.searchInput.addEventListener('input', handleSearchInput);
  dom.searchInput.addEventListener('focus', () => {
    filterDropdown(dom.searchInput.value.trim());
    dom.dropdown.style.display = 'block';
  });

  dom.clearBtn.addEventListener('click', () => {
    dom.searchInput.value = '';
    dom.clearBtn.style.display = 'none';
    filterDropdown('');
    dom.searchInput.focus();
  });

  // Cerrar dropdown al hacer clic fuera
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-box-container')) {
      dom.dropdown.style.display = 'none';
    }
  });

  // Navegación por teclado en el input de búsqueda
  dom.searchInput.addEventListener('keydown', handleKeyNavigation);

  // Tabs de Gráfico y Tabla
  dom.tabChartBtn.addEventListener('click', () => switchTab('chart'));
  dom.tabTableBtn.addEventListener('click', () => switchTab('table'));

  // Botones de Exportación
  dom.downloadDocxBtn.addEventListener('click', downloadDocx);
  dom.downloadPdfBtn.addEventListener('click', downloadPdf);
  dom.copyReportBtn.addEventListener('click', copyFullReportText);
  dom.copyPaperTextBtn.addEventListener('click', copyFullReportText);
  dom.printBtn.addEventListener('click', () => window.print());
}

// ============================================================
// CARGA DE PAÍSES Y RENDERIZADO DEL SELECTOR
// ============================================================
async function loadCountries() {
  try {
    const res = await fetch('/api/countries');
    const data = await res.json();
    AppState.countries = data.countries || [];
    
    renderQuickChips();
    filterDropdown('');
  } catch (err) {
    console.error('Error al cargar países:', err);
    showToast('Error al conectar con el servidor', true);
  }
}

function renderQuickChips() {
  const frequentList = ['Uruguay', 'Estados Unidos', 'China', 'España', 'Países Bajos', 'Alemania', 'Chile', 'Colombia', 'México', 'Canadá', 'Brasil', 'Italia', 'Japón'];
  
  dom.chipsContainer.innerHTML = '';
  frequentList.forEach(countryName => {
    const exists = AppState.countries.find(c => c.name.toLowerCase() === countryName.toLowerCase());
    if (exists) {
      const chip = document.createElement('button');
      chip.className = `country-chip ${countryName.toLowerCase() === AppState.selectedCountry.toLowerCase() ? 'active' : ''}`;
      chip.textContent = countryName;
      chip.addEventListener('click', () => selectCountry(exists.name));
      dom.chipsContainer.appendChild(chip);
    }
  });
}

function updateActiveChip() {
  document.querySelectorAll('.country-chip').forEach(chip => {
    if (chip.textContent.trim().toLowerCase() === AppState.selectedCountry.toLowerCase()) {
      chip.classList.add('active');
    } else {
      chip.classList.remove('active');
    }
  });
}

function filterDropdown(query) {
  const q = query.toLowerCase();
  const filtered = AppState.countries.filter(c => c.name.toLowerCase().includes(q));

  dom.dropdown.innerHTML = '';
  
  if (filtered.length === 0) {
    const emptyItem = document.createElement('div');
    emptyItem.className = 'dropdown-item';
    emptyItem.style.color = '#9CA3AF';
    emptyItem.textContent = 'No se encontraron países con ese nombre';
    dom.dropdown.appendChild(emptyItem);
    return;
  }

  filtered.forEach((c) => {
    const item = document.createElement('div');
    item.className = `dropdown-item ${c.name.toLowerCase() === AppState.selectedCountry.toLowerCase() ? 'active' : ''}`;
    
    const fobTxt = c.fob_2025 > 0 ? (c.fob_2025 >= 1e6 ? `$${(c.fob_2025/1e6).toFixed(1)}M` : `$${(c.fob_2025/1e3).toFixed(0)}k`) : '$0';
    
    item.innerHTML = `
      <span class="dropdown-item-name">${c.name}</span>
      <div class="dropdown-item-badges">
        ${c.rutex_companies > 0 ? `<span class="badge-rutex-sm">${c.rutex_companies} emp.</span>` : ''}
        ${c.fob_2025 > 0 ? `<span class="badge-fob-sm">${fobTxt}</span>` : ''}
      </div>
    `;

    item.addEventListener('click', () => {
      selectCountry(c.name);
      dom.dropdown.style.display = 'none';
    });

    dom.dropdown.appendChild(item);
  });
}

function handleSearchInput(e) {
  const query = e.target.value;
  dom.clearBtn.style.display = query ? 'flex' : 'none';
  filterDropdown(query.trim());
  dom.dropdown.style.display = 'block';
}

function handleKeyNavigation(e) {
  const items = dom.dropdown.querySelectorAll('.dropdown-item:not([style*="color"])');
  if (!items.length) return;

  let activeIndex = -1;
  items.forEach((item, idx) => {
    if (item.classList.contains('active')) activeIndex = idx;
  });

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    dom.dropdown.style.display = 'block';
    const nextIndex = activeIndex < items.length - 1 ? activeIndex + 1 : 0;
    highlightDropdownItem(items, nextIndex);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    dom.dropdown.style.display = 'block';
    const prevIndex = activeIndex > 0 ? activeIndex - 1 : items.length - 1;
    highlightDropdownItem(items, prevIndex);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (activeIndex >= 0 && items[activeIndex]) {
      items[activeIndex].click();
    }
  } else if (e.key === 'Escape') {
    dom.dropdown.style.display = 'none';
  }
}

function highlightDropdownItem(items, index) {
  items.forEach(it => it.classList.remove('active'));
  const current = items[index];
  if (current) {
    current.classList.add('active');
    current.scrollIntoView({ block: 'nearest' });
  }
}

// ============================================================
// SELECCIÓN Y CARGA DEL REPORTE DEL PAÍS
// ============================================================
async function selectCountry(countryName) {
  if (!countryName) return;

  AppState.selectedCountry = countryName;
  dom.searchInput.value = countryName;
  dom.clearBtn.style.display = 'flex';
  dom.dropdown.style.display = 'none';
  updateActiveChip();

  // Mostrar loading
  dom.loadingOverlay.style.display = 'flex';
  dom.reportContent.style.opacity = '0.4';

  try {
    const encoded = encodeURIComponent(countryName);
    const res = await fetch(`/api/report?country=${encoded}`);
    if (!res.ok) throw new Error('Error al obtener reporte del país');
    const report = await res.json();
    AppState.currentReport = report;

    renderReport(report);
  } catch (err) {
    console.error('Error al cargar reporte:', err);
    showToast('Error al procesar la información del país', true);
  } finally {
    dom.loadingOverlay.style.display = 'none';
    dom.reportContent.style.opacity = '1';
  }
}

// ============================================================
// RENDERIZADO DEL REPORTE COMPLETO
// ============================================================
function renderReport(report) {
  const m = report.metrics;
  const p = report.paragraphs;

  // 1. Banner
  dom.countryTitle.textContent = report.country_display || report.country;
  dom.countryMetaSubtitle.textContent = `Empresas exportadoras en Ruta Exportadora — Periodo 2024 / 2025 / 2026`;

  // 2. KPIs
  dom.kpiEmpresas.textContent = m.cant_empresas_rutex.toLocaleString('es-PE');
  dom.kpiPartidas.textContent = m.cant_productos_rutex.toLocaleString('es-PE');
  
  dom.kpiFob2025.textContent = `USD ${m.fob_2025_millones.toFixed(1)}M`;
  dom.kpiFob2025Exacto.textContent = `FOB Total: US$ ${m.fob_2025_total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  dom.kpiFob2024.textContent = `USD ${m.fob_2024_millones.toFixed(1)}M`;
  dom.kpiFob2024Exacto.textContent = `FOB Total: US$ ${m.fob_2024_total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const varSign = m.is_positive ? '+' : '';
  dom.kpiVarPct.textContent = `${varSign}${m.var_pct.toFixed(2)}%`;
  
  if (m.is_positive) {
    dom.kpiVarTipo.textContent = 'Incremento interanual';
    dom.kpiVarTipo.className = 'var-badge var-positive';
    dom.kpiVarIcon.innerHTML = '<i class="fa-solid fa-arrow-trend-up text-accent" style="color: #16A34A;"></i>';
  } else {
    dom.kpiVarTipo.textContent = 'Disminución interanual';
    dom.kpiVarTipo.className = 'var-badge var-negative';
    dom.kpiVarIcon.innerHTML = '<i class="fa-solid fa-arrow-trend-down text-accent" style="color: #DC2626;"></i>';
  }

  // 3. Documento Oficial
  dom.docTitle.textContent = report.title;
  dom.docSubtitle.textContent = report.subtitle;
  dom.docP1.textContent = p.p1;
  dom.docP2.textContent = p.p2;
  dom.docEventsHeading.textContent = p.events_heading;

  dom.docEventsBullets.innerHTML = '';
  if (p.events_bullets && p.events_bullets.length > 0) {
    p.events_bullets.forEach(txt => {
      const li = document.createElement('li');
      li.textContent = txt;
      dom.docEventsBullets.appendChild(li);
    });
  } else {
    const li = document.createElement('li');
    li.textContent = "No se registraron eventos o programas para las empresas exportadoras a este destino.";
    dom.docEventsBullets.appendChild(li);
  }

  // 4. Top 5 Productos
  renderTopProducts(report.top_productos);

  // 5. Top 5 Regiones
  renderTopRegions(report.top_regiones);

  // 6. Top 15 Eventos (Gráfico y Tabla)
  renderEventsChart(report.top_eventos);
  renderEventsTable(report.top_eventos);
}

function renderTopProducts(products) {
  dom.topProductsList.innerHTML = '';
  if (!products || products.length === 0) {
    dom.topProductsList.innerHTML = '<p style="color: #9CA3AF; font-size: 0.85rem;">Sin registros de productos para este mercado.</p>';
    return;
  }

  products.forEach(p => {
    const row = document.createElement('div');
    row.className = 'top-item-row';
    row.innerHTML = `
      <div class="top-item-meta">
        <span class="top-item-title" title="${p.partida}">${p.descripcion_limpia}</span>
        <span class="top-item-val">${p.fob_formatted} (${p.share_pct}%)</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width: ${Math.min(100, Math.max(5, p.share_pct))}%;"></div>
      </div>
    `;
    dom.topProductsList.appendChild(row);
  });
}

function renderTopRegions(regions) {
  dom.topRegionsList.innerHTML = '';
  if (!regions || regions.length === 0) {
    dom.topRegionsList.innerHTML = '<p style="color: #9CA3AF; font-size: 0.85rem;">Sin registros regionales para este mercado.</p>';
    return;
  }

  regions.forEach(r => {
    const row = document.createElement('div');
    row.className = 'top-item-row';
    const empWord = r.empresas === 1 ? 'empresa' : 'empresas';
    row.innerHTML = `
      <div class="top-item-meta">
        <span class="top-item-title"><strong>${r.region}</strong> (${r.empresas} ${empWord})</span>
        <span class="top-item-val">${r.fob_formatted} (${r.share_pct}%)</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width: ${Math.min(100, Math.max(5, r.share_pct))}%; background: #003366;"></div>
      </div>
    `;
    dom.topRegionsList.appendChild(row);
  });
}

// ============================================================
// VISUALIZACIÓN DE EVENTOS TOP 15: CHART & TABLE
// ============================================================
function renderEventsChart(events) {
  if (AppState.chartInstance) {
    AppState.chartInstance.destroy();
  }

  if (!events || events.length === 0) {
    return;
  }

  // Ordenar para el gráfico horizontal (los más altos arriba)
  const labels = events.map(e => {
    // Truncar texto para las etiquetas si es muy largo
    const full = e.evento;
    return full.length > 55 ? full.substring(0, 52) + '...' : full;
  });
  const data = events.map(e => e.empresas);

  const ctx = dom.chartCanvas.getContext('2d');

  // Gradiente institucional PROMPERÚ
  const gradient = ctx.createLinearGradient(0, 0, 400, 0);
  gradient.addColorStop(0, '#D12628');
  gradient.addColorStop(1, '#E65100');

  AppState.chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Empresas Participantes',
        data: data,
        backgroundColor: gradient,
        borderRadius: 6,
        borderSkipped: false,
        barPercentage: 0.72,
        categoryPercentage: 0.85
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: '#111827',
          titleFont: { size: 12, family: 'Inter', weight: 'bold' },
          bodyFont: { size: 12, family: 'Inter' },
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            title: function(items) {
              const idx = items[0].dataIndex;
              return events[idx].evento;
            },
            label: function(context) {
              const val = context.raw;
              return `${val} ${val === 1 ? 'empresa participante' : 'empresas participantes'}`;
            }
          }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            precision: 0,
            font: { family: 'Inter', size: 11 },
            color: '#6B7280'
          },
          grid: {
            color: '#F3F4F6'
          }
        },
        y: {
          ticks: {
            font: { family: 'Inter', size: 11, weight: '500' },
            color: '#1F2937'
          },
          grid: {
            display: false
          }
        }
      }
    }
  });
}

function renderEventsTable(events) {
  dom.eventsTableBody.innerHTML = '';
  if (!events || events.length === 0) {
    dom.eventsTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #9CA3AF; padding: 2rem;">No se registraron programas o eventos en Rutex.</td></tr>';
    return;
  }

  const maxVal = Math.max(...events.map(e => e.empresas), 1);

  events.forEach((ev) => {
    const tr = document.createElement('tr');
    
    let rankClass = '';
    if (ev.rank === 1) rankClass = 'rank-1';
    else if (ev.rank === 2) rankClass = 'rank-2';
    else if (ev.rank === 3) rankClass = 'rank-3';

    const pct = Math.round((ev.empresas / maxVal) * 100);

    tr.innerHTML = `
      <td style="text-align: center;">
        <span class="rank-badge ${rankClass}">${ev.rank}</span>
      </td>
      <td>
        <strong>${ev.evento}</strong>
      </td>
      <td style="text-align: center;">
        <span class="badge-count">${ev.empresas} ${ev.empresas === 1 ? 'empresa' : 'empresas'}</span>
      </td>
      <td style="text-align: center;">
        <div class="progress-track" style="margin: 0 auto; width: 100px;">
          <div class="progress-fill" style="width: ${pct}%;"></div>
        </div>
      </td>
    `;
    dom.eventsTableBody.appendChild(tr);
  });
}

function switchTab(target) {
  if (target === 'chart') {
    dom.tabChartBtn.classList.add('active');
    dom.tabTableBtn.classList.remove('active');
    dom.chartView.style.display = 'block';
    dom.tableView.style.display = 'none';
  } else {
    dom.tabTableBtn.classList.add('active');
    dom.tabChartBtn.classList.remove('active');
    dom.chartView.style.display = 'none';
    dom.tableView.style.display = 'block';
  }
}

// ============================================================
// DESCARGA Y EXPORTACIÓN
// ============================================================
function downloadDocx() {
  if (!AppState.selectedCountry) return;
  const encoded = encodeURIComponent(AppState.selectedCountry);
  const url = `/api/export/docx?country=${encoded}`;
  
  showToast('Iniciando descarga de documento Word (.docx)...');
  triggerFileDownload(url, `Ayuda_Memoria_Exportaciones_${AppState.selectedCountry.replace(/ /g, '_')}.docx`);
}

function downloadPdf() {
  if (!AppState.selectedCountry) return;
  const encoded = encodeURIComponent(AppState.selectedCountry);
  const url = `/api/export/pdf?country=${encoded}`;
  
  showToast('Generando reporte institucional en PDF...');
  triggerFileDownload(url, `Ayuda_Memoria_Exportaciones_${AppState.selectedCountry.replace(/ /g, '_')}.pdf`);
}

function triggerFileDownload(url, filename) {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function copyFullReportText() {
  if (!AppState.currentReport) return;
  
  const r = AppState.currentReport;
  const p = r.paragraphs;

  let textToCopy = `${r.title}\n${r.subtitle}\n\n`;
  textToCopy += `${p.p1}\n\n`;
  textToCopy += `${p.p2}\n\n`;
  textToCopy += `${p.events_heading}\n`;

  if (p.events_bullets && p.events_bullets.length > 0) {
    p.events_bullets.forEach(b => {
      textToCopy += `• ${b}\n`;
    });
  }

  navigator.clipboard.writeText(textToCopy).then(() => {
    showToast('¡Texto oficial copiado al portapapeles!');
  }).catch(err => {
    console.error('Error al copiar texto:', err);
    showToast('No se pudo copiar automáticamente', true);
  });
}

function showToast(msg, isError = false) {
  dom.toastMessage.textContent = msg;
  dom.toast.querySelector('.toast-icon').className = isError 
    ? 'fa-solid fa-circle-exclamation toast-icon' 
    : 'fa-solid fa-check-circle toast-icon';
  dom.toast.querySelector('.toast-icon').style.color = isError ? '#DC2626' : '#16A34A';

  dom.toast.classList.add('show');
  setTimeout(() => {
    dom.toast.classList.remove('show');
  }, 3200);
}
