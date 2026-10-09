import os
import re
import time
import pandas as pd
import numpy as np

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RUTEX_FILE = os.path.join(BASE_DIR, "base rutex 29.09.2026 - Colab.xlsx")
EXP_2024_FILE = os.path.join(BASE_DIR, "EXPORTACIONES 2024.xlsx")
EXP_2025_FILE = os.path.join(BASE_DIR, "EXPORTACIONES 2025.xlsx")

def limpiar_ruc(series: pd.Series) -> pd.Series:
    """Limpia la columna RUC para asegurar consistencia"""
    return series.astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

def limpiar_monto(series: pd.Series) -> pd.Series:
    """Convierte importes a numérico"""
    return pd.to_numeric(series.astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0.0)

def formatear_monto_texto(val: float) -> str:
    """Formatea valores monetarios a texto estilo informe oficial"""
    if val >= 1_000_000:
        v_m = val / 1_000_000
        return f"US$ {int(v_m)} millones" if v_m.is_integer() else f"US$ {v_m:.1f} millones"
    elif val >= 1_000:
        v_k = val / 1_000
        return f"USD {int(v_k)} mil" if v_k.is_integer() else f"USD {v_k:.0f} mil"
    else:
        return f"USD {int(val)}"

def limpiar_codigo_producto(nombre_producto: str) -> str:
    """Reemplaza cualquier número inicial seguido de un guion opcional y espacios"""
    return re.sub(r'^\d+\s*-\s*', '', str(nombre_producto)).strip()

class DataStore:
    _instance = None

    def __init__(self):
        self.df_rutex: pd.DataFrame = None
        self.df_exp_2024: pd.DataFrame = None
        self.df_exp_2025: pd.DataFrame = None
        self.rucs_rutex: set = set()
        self.countries: list[dict] = []
        self._initialized = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DataStore()
            cls._instance.initialize()
        return cls._instance

    def initialize(self, force_reload: bool = False):
        if self._initialized and not force_reload:
            return

        os.makedirs(CACHE_DIR, exist_ok=True)
        rutex_cache = os.path.join(CACHE_DIR, "rutex.pkl")
        exp_2024_cache = os.path.join(CACHE_DIR, "exp_2024.pkl")
        exp_2025_cache = os.path.join(CACHE_DIR, "exp_2025.pkl")

        need_build_cache = force_reload or not (
            os.path.exists(rutex_cache) and 
            os.path.exists(exp_2024_cache) and 
            os.path.exists(exp_2025_cache)
        )

        if not need_build_cache:
            # Check modification dates
            rutex_mtime = os.path.getmtime(RUTEX_FILE) if os.path.exists(RUTEX_FILE) else 0
            exp_2024_mtime = os.path.getmtime(EXP_2024_FILE) if os.path.exists(EXP_2024_FILE) else 0
            exp_2025_mtime = os.path.getmtime(EXP_2025_FILE) if os.path.exists(EXP_2025_FILE) else 0
            cache_mtime = min(os.path.getmtime(rutex_cache), os.path.getmtime(exp_2024_cache), os.path.getmtime(exp_2025_cache))
            if cache_mtime < max(rutex_mtime, exp_2024_mtime, exp_2025_mtime):
                need_build_cache = True

        if need_build_cache:
            print("[DataStore] Generando caché binaria optimizada desde archivos Excel...")
            t0 = time.time()
            df_rutex = pd.read_excel(RUTEX_FILE)
            df_exp_2024 = pd.read_excel(EXP_2024_FILE)
            df_exp_2025 = pd.read_excel(EXP_2025_FILE)

            # Limpieza y estandarización
            df_rutex['RUC_CLEAN'] = limpiar_ruc(df_rutex['RUC'])
            df_exp_2024['RUC_CLEAN'] = limpiar_ruc(df_exp_2024['RUC'])
            df_exp_2025['RUC_CLEAN'] = limpiar_ruc(df_exp_2025['RUC'])

            df_exp_2024['FOB USD'] = limpiar_monto(df_exp_2024['FOB USD'])
            df_exp_2025['FOB USD'] = limpiar_monto(df_exp_2025['FOB USD'])

            df_exp_2024['MERCADO'] = df_exp_2024['MERCADO'].astype(str).str.strip()
            df_exp_2025['MERCADO'] = df_exp_2025['MERCADO'].astype(str).str.strip()

            # Guardar pickle
            df_rutex.to_pickle(rutex_cache)
            df_exp_2024.to_pickle(exp_2024_cache)
            df_exp_2025.to_pickle(exp_2025_cache)
            print(f"[DataStore] Caché generada en {time.time() - t0:.2f}s")
        else:
            print("[DataStore] Cargando datos desde caché rápida...")

        t0 = time.time()
        self.df_rutex = pd.read_pickle(rutex_cache)
        self.df_exp_2024 = pd.read_pickle(exp_2024_cache)
        self.df_exp_2025 = pd.read_pickle(exp_2025_cache)
        self.rucs_rutex = set(self.df_rutex['RUC_CLEAN'].dropna().unique())
        print(f"[DataStore] Datos cargados en memoria en {time.time() - t0:.2f}s")

        self._build_country_list()
        self._initialized = True

        # Sincronización automática de Ayuda_Memoria_País_PROMPERU_2026.html si la BD cambió
        standalone_html = os.path.join(BASE_DIR, "Ayuda_Memoria_País_PROMPERU_2026.html")
        if need_build_cache or not os.path.exists(standalone_html):
            try:
                print("[DataStore] BD actualizada detectada. Auto-sincronizando Ayuda_Memoria_País_PROMPERU_2026.html...")
                from build_standalone import build_standalone
                build_standalone()
            except Exception as err:
                print(f"[DataStore] Advertencia en auto-sincronización de HTML autónomo: {err}")

    def _build_country_list(self):
        """Construye la lista ordenada de países disponibles con metadatos rápidos"""
        # Mercados presentes en 2025 y 2024
        m25 = set(self.df_exp_2025['MERCADO'].dropna().unique())
        m24 = set(self.df_exp_2024['MERCADO'].dropna().unique())
        all_markets = sorted(list(m25.union(m24)))

        # Pre-calcular empresas de Rutex y FOB 2025 por mercado para badges en el combo
        exp25_rutex = self.df_exp_2025[self.df_exp_2025['RUC_CLEAN'].isin(self.rucs_rutex)]
        agg_2025 = exp25_rutex.groupby('MERCADO').agg(
            empresas=('RUC_CLEAN', 'nunique'),
            fob=('FOB USD', 'sum')
        ).to_dict(orient='index')

        country_list = []
        for m in all_markets:
            if not m or m.lower() == 'nan':
                continue
            meta = agg_2025.get(m, {'empresas': 0, 'fob': 0.0})
            country_list.append({
                'name': m,
                'rutex_companies': int(meta['empresas']),
                'fob_2025': float(meta['fob'])
            })

        # Ordenar: primero los que tienen empresas Rutex (ordenados por FOB desc), luego alfabéticamente
        country_list.sort(key=lambda x: (-x['rutex_companies'], -x['fob_2025'], x['name']))
        self.countries = country_list

    def get_report(self, country_name: str) -> dict:
        """
        Calcula exactamente todas las métricas, textos oficiales y tops
        para el país especificado según la lógica de la Ayuda Memoria.
        """
        country_clean = country_name.strip()
        country_upper = country_clean.upper()

        # Filtrar exportaciones por país (case-insensitive)
        mask_2024 = self.df_exp_2024['MERCADO'].astype(str).str.strip().str.upper() == country_upper
        mask_2025 = self.df_exp_2025['MERCADO'].astype(str).str.strip().str.upper() == country_upper

        df_2024_p = self.df_exp_2024[mask_2024]
        df_2025_p = self.df_exp_2025[mask_2025]

        # Cruzar con Rutex
        df_2024_p_rutex = df_2024_p[df_2024_p['RUC_CLEAN'].isin(self.rucs_rutex)]
        df_2025_p_rutex = df_2025_p[df_2025_p['RUC_CLEAN'].isin(self.rucs_rutex)]

        # Filtrar Rutex para empresas exportadoras a ese país en 2025
        rucs_exportadores_2025_rutex = set(df_2025_p_rutex['RUC_CLEAN'].dropna().unique())
        df_rutex_p = self.df_rutex[self.df_rutex['RUC_CLEAN'].isin(rucs_exportadores_2025_rutex)]

        # 1. Métricas clave
        cant_empresas_rutex = int(df_rutex_p['RUC_CLEAN'].nunique())
        cant_productos_rutex = int(df_2025_p_rutex['PARTIDA_DESCRIP_LARGA'].nunique())

        fob_2024_total = float(df_2024_p_rutex['FOB USD'].sum())
        fob_2025_total = float(df_2025_p_rutex['FOB USD'].sum())

        fob_2024_millones = fob_2024_total / 1_000_000.0
        fob_2025_millones = fob_2025_total / 1_000_000.0

        if fob_2024_total > 0:
            var_pct = ((fob_2025_total - fob_2024_total) / fob_2024_total) * 100.0
        else:
            var_pct = 0.0

        tipo_var = "disminución" if var_pct < 0 else "incremento"
        abs_var_pct = abs(var_pct)

        # 2. Top 5 Productos 2025 (Cruce Rutex)
        top_prod_df = (
            df_2025_p_rutex.groupby('PARTIDA_DESCRIP_LARGA')['FOB USD']
            .sum()
            .reset_index()
            .sort_values(by='FOB USD', ascending=False)
            .head(5)
        )

        top_productos = []
        prod_textos = []
        for _, row in top_prod_df.iterrows():
            partida_desc = str(row['PARTIDA_DESCRIP_LARGA']).strip()
            p_nom_limpio = limpiar_codigo_producto(partida_desc).lower()
            monto = float(row['FOB USD'])
            p_monto_txt = formatear_monto_texto(monto)
            share = (monto / fob_2025_total * 100.0) if fob_2025_total > 0 else 0.0

            top_productos.append({
                'partida': partida_desc,
                'descripcion_limpia': p_nom_limpio,
                'fob': monto,
                'fob_formatted': p_monto_txt,
                'share_pct': round(share, 2)
            })
            prod_textos.append(f"{p_monto_txt} en {p_nom_limpio}")

        texto_productos = ", ".join(prod_textos) if prod_textos else "sin registros de productos"

        # 3. Top 5 Regiones 2025 (DEPARTAMENTO en Exportaciones 2025 cruzada con Rutex)
        top_reg_df = (
            df_2025_p_rutex.groupby('DEPARTAMENTO')
            .agg(fob=('FOB USD', 'sum'), empresas=('RUC_CLEAN', 'nunique'))
            .reset_index()
            .sort_values(by='fob', ascending=False)
            .head(5)
        )

        top_regiones = []
        reg_textos = []
        for _, row in top_reg_df.iterrows():
            r_nom = str(row['DEPARTAMENTO']).strip().title()
            r_fob = float(row['fob'])
            r_monto_txt = formatear_monto_texto(r_fob)
            r_emp = int(row['empresas'])
            emp_word = "empresa" if r_emp == 1 else "empresas"
            share = (r_fob / fob_2025_total * 100.0) if fob_2025_total > 0 else 0.0

            top_regiones.append({
                'region': r_nom,
                'fob': r_fob,
                'fob_formatted': r_monto_txt,
                'empresas': r_emp,
                'share_pct': round(share, 2)
            })
            reg_textos.append(f"{r_nom} ({r_monto_txt} / {r_emp} {emp_word})")

        texto_regiones = ", ".join(reg_textos) if reg_textos else "sin registros regionales"

        # 4. Top 15 Eventos / Programas en Rutex
        top_ev_df = (
            df_rutex_p.groupby('EVENTO')['RUC_CLEAN']
            .nunique()
            .reset_index()
            .rename(columns={'RUC_CLEAN': 'CANT_EMPRESAS'})
            .sort_values(by='CANT_EMPRESAS', ascending=False)
            .head(15)
        )

        top_eventos = []
        eventos_bullet_texts = []
        for idx, row in top_ev_df.iterrows():
            ev_nom = str(row['EVENTO']).strip()
            num_emp = int(row['CANT_EMPRESAS'])
            emp_label = "empresa participante" if num_emp == 1 else "empresas participantes"
            top_eventos.append({
                'rank': len(top_eventos) + 1,
                'evento': ev_nom,
                'empresas': num_emp,
                'label': f"{ev_nom}: {num_emp} {emp_label}"
            })
            eventos_bullet_texts.append(f"{ev_nom}: {num_emp} {emp_label}")

        # 5. Redacción oficial de Párrafos
        pais_titulo = country_clean.title()
        # Tratamiento especial de mayúsculas para países conocidos como EE.UU. o con artículos
        if country_upper in ['ESTADOS UNIDOS', 'EE.UU.', 'EEUU']:
            pais_titulo = "Estados Unidos"

        parrafo_1 = (
            f"Durante el 2026 se atendieron a {cant_empresas_rutex} empresas exportadoras que atienden al mercado de {country_clean.capitalize()}, "
            f"a través de {cant_productos_rutex} productos (número de partidas únicas), el monto exportado en el 2025 (enero-diciembre) "
            f"fue de USD {fob_2025_millones:.1f} millones y en el 2024 fue USD {fob_2024_millones:.1f} millones, con lo que se observó "
            f"una {tipo_var} de {abs_var_pct:.2f}% con respecto al año anterior."
        )

        parrafo_2 = (
            f"Los principales productos exportados en el 2025 fueron {texto_productos}. "
            f"Las principales regiones exportadoras son {texto_regiones}."
        )

        titulo_doc = "Ayuda memoria"
        subtitulo_doc = f"Empresas exportadoras a {country_clean.capitalize()} - Ruta Exportadora"
        encabezado_eventos = "Los principales programas en donde participaron las empresas fueron:"

        return {
            'country': country_clean,
            'country_display': country_clean.capitalize(),
            'title': titulo_doc,
            'subtitle': subtitulo_doc,
            'metrics': {
                'cant_empresas_rutex': cant_empresas_rutex,
                'cant_productos_rutex': cant_productos_rutex,
                'fob_2024_total': fob_2024_total,
                'fob_2025_total': fob_2025_total,
                'fob_2024_millones': round(fob_2024_millones, 2),
                'fob_2025_millones': round(fob_2025_millones, 2),
                'var_pct': round(var_pct, 2),
                'tipo_var': tipo_var,
                'abs_var_pct': round(abs_var_pct, 2),
                'is_positive': var_pct >= 0
            },
            'paragraphs': {
                'p1': parrafo_1,
                'p2': parrafo_2,
                'events_heading': encabezado_eventos,
                'events_bullets': eventos_bullet_texts
            },
            'top_productos': top_productos,
            'top_regiones': top_regiones,
            'top_eventos': top_eventos
        }
