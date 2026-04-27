import streamlit as st
import requests
import pandas as pd
import io
import json
import time

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Presupuesto Express",
    page_icon="🏛️",
    layout="wide",
)

# ─────────────────────────────────────────────
# SECRETS
# ─────────────────────────────────────────────
def get_secret(name: str, default: str = "") -> str:
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

APP_ACCESS_CODE = get_secret("APP_ACCESS_CODE")
PRESUPUESTO_API_KEY = get_secret("PRESUPUESTO_API_KEY")

if not APP_ACCESS_CODE or not PRESUPUESTO_API_KEY:
    st.error(
        "Faltan configurar secrets en Streamlit Cloud. "
        "Agregá APP_ACCESS_CODE y PRESUPUESTO_API_KEY en Settings → Secrets."
    )
    st.stop()

codigo_ingresado = st.text_input("Código de acceso", type="password")
if codigo_ingresado != APP_ACCESS_CODE:
    st.warning("Ingresá el código de acceso para usar la app.")
    st.stop()

GOOGLE_SHEET_ID = "1vT5nCBy1lbh4KNxmQhxclhkHsGiO5qB_m0PkyaWtlrs"
GOOGLE_SHEET_BASE = (
    f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet="
)

# ─────────────────────────────────────────────
# DEFINICIÓN DE ENDPOINTS
# ─────────────────────────────────────────────
ENDPOINT_CONFIG = {
    "credito": {
        "label": "💰 Crédito",
        "url": "https://www.presupuestoabierto.gob.ar/api/v1/credito",
        "columnas_monto": [
            "credito_presupuestado",
            "credito_vigente",
            "credito_comprometido",
            "credito_devengado",
            "credito_pagado",
        ],
        # Columna que se ajusta en modo mensual
        "col_devengado_mensual": "credito_devengado",
        "permite_inflacion": True,
        "columnas_clasificacion": {
            "📅 Temporales": [
                "impacto_presupuestario_fecha",
                "impacto_presupuestario_anio",
                "impacto_presupuestario_mes",
                "ejercicio_presupuestario",
            ],
            "🏛️ Institucional": [
                "sector_id", "sector_desc",
                "subsector_id", "subsector_desc",
                "caracter_id", "caracter_desc",
                "jurisdiccion_id", "jurisdiccion_desc",
                "subjurisdiccion_id", "subjurisdiccion_desc",
                "entidad_id", "entidad_desc",
                "unidad_ejecutora_id", "unidad_ejecutora_desc",
            ],
            "📋 Programática": [
                "servicio_id", "servicio_desc",
                "programa_id", "programa_desc",
                "subprograma_id", "subprograma_desc",
                "proyecto_id", "proyecto_desc",
                "actividad_id", "actividad_desc",
                "obra_id", "obra_desc",
            ],
            "💰 Económica": [
                "inciso_id", "inciso_desc",
                "principal_id", "principal_desc",
                "parcial_id", "parcial_desc",
                "subparcial_id", "subparcial_desc",
                "clasificador_economico_8_digitos_id",
                "clasificador_economico_8_digitos_desc",
            ],
            "🗺️ Geográfica / Financiera": [
                "finalidad_id", "finalidad_desc",
                "funcion_id", "funcion_desc",
                "fuente_financiamiento_id", "fuente_financiamiento_desc",
                "ubicacion_geografica_id", "ubicacion_geografica_desc",
                "prestamo_externo_id", "prestamo_externo_desc",
                "codigo_bapin_id", "codigo_bapin_desc",
            ],
        },
        "default_columns": [
            "impacto_presupuestario_anio",
            "jurisdiccion_desc",
            "programa_desc",
            "actividad_desc",
            "credito_presupuestado",
            "credito_vigente",
            "credito_devengado",
        ],
    },

    "recurso": {
        "label": "📥 Recurso",
        "url": "https://www.presupuestoabierto.gob.ar/api/v1/recurso",
        "columnas_monto": [
            "recurso_inicial",
            "recurso_vigente",
            "recurso_ingresado_percibido",
        ],
        "col_devengado_mensual": "recurso_ingresado_percibido",
        "permite_inflacion": True,
        "columnas_clasificacion": {
            "📅 Temporales": [
                "impacto_presupuestario_fecha",
                "impacto_presupuestario_anio",
                "impacto_presupuestario_mes",
                "ejercicio_presupuestario",
            ],
            "🏛️ Institucional": [
                "sector_id", "sector_desc",
                "subsector_id", "subsector_desc",
                "caracter_id", "caracter_desc",
                "jurisdiccion_id", "jurisdiccion_desc",
                "subjurisdiccion_id", "subjurisdiccion_desc",
                "entidad_id", "entidad_desc",
                "servicio_id", "servicio_desc",
            ],
            "📋 Tipo / Clase / Concepto": [
                "tipo_id", "tipo_desc",
                "clase_id", "clase_desc",
                "concepto_id", "concepto_desc",
                "subconcepto_id", "subconcepto_desc",
            ],
            "🗺️ Financiera": [
                "fuente_financiamiento_id", "fuente_financiamiento_desc",
                "clasificador_economico_8_digitos_id",
                "clasificador_economico_8_digitos_desc",
                "prestamo_externo_id", "prestamo_externo_desc",
                "ultima_actualizacion_fecha",
            ],
        },
        "default_columns": [
            "impacto_presupuestario_anio",
            "jurisdiccion_desc",
            "tipo_desc",
            "concepto_desc",
            "recurso_inicial",
            "recurso_vigente",
            "recurso_ingresado_percibido",
        ],
    },

    "pef": {
        "label": "📊 Ejec. Física",
        "url": "https://www.presupuestoabierto.gob.ar/api/v1/pef",
        "columnas_monto": [
            "totalizador_avance_fisico",
            "programacion_inicial_DA",
            "programacion_inicial_ajustada",
            "programacion_anual_vig_cierre",
            "programacion_anual_vig_trim",
            "programacion_trim",
            "programacion_acumulada_trim",
            "ejecutado_vigente_trim",
            "ejecutado_acumulado_trim",
            "ejecutado_cierre_acum_trim",
            "ejecucion_anual_de_cierre",
        ],
        "col_devengado_mensual": None,
        "permite_inflacion": False,
        "columnas_clasificacion": {
            "📅 Temporales": [
                "ejercicio_presupuestario",
                "trimestre",
            ],
            "🏛️ Institucional": [
                "finalidad_id", "finalidad_desc",
                "funcion_id", "funcion_desc",
                "sector_id", "sector_desc",
                "subsector_id", "subsector_desc",
                "caracter_id", "caracter_desc",
                "jurisdiccion_id", "jurisdiccion_desc",
                "subjurisdiccion_id", "subjurisdiccion_desc",
                "entidad_id", "entidad_desc",
                "servicio_id", "servicio_desc",
            ],
            "📋 Programática": [
                "programa_id", "programa_desc",
                "subprograma_id", "subprograma_desc",
                "proyecto_id", "proyecto_desc",
                "actividad_id", "actividad_desc",
                "obra_id", "obra_desc",
            ],
            "📏 Medición Física": [
                "medicion_fisica_id", "medicion_fisica_desc",
                "tipo_medicion_fisica",
                "unidad_medida_id", "unidad_medida_desc",
                "ubicacion_geografica_id", "ubicacion_geografica_desc",
            ],
            "⚠️ Desvíos": [
                "tipo_causa_desvio",
                "causa_desvio",
                "causa_desvio_detalle",
                "causa_desvio_comentario",
                "porc_desvio_acum_trim",
                "ultima_actualizacion_fecha",
            ],
        },
        "default_columns": [
            "ejercicio_presupuestario",
            "trimestre",
            "jurisdiccion_desc",
            "programa_desc",
            "actividad_desc",
            "medicion_fisica_desc",
            "programacion_trim",
            "ejecutado_acumulado_trim",
        ],
    },
}

OPERADORES_UNO = {
    "igual a": "equal",
    "contiene (like)": "like",
    "mayor que": "greater_than",
    "mayor o igual que": "greater_equal_than",
    "menor que": "lower_than",
    "menor o igual que": "lower_equal_than",
}
OPERADORES_DOS = {"entre": "between"}


# ─────────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
  html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
  .main { background: #0d1117; }
  h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; }
  .stButton > button {
      background: #58a6ff; color: #0d1117;
      font-family: 'IBM Plex Mono', monospace; font-weight: 600;
      border: none; border-radius: 4px; padding: 0.5rem 1.5rem;
  }
  .stButton > button:hover { background: #79c0ff; }
  div[data-testid="stExpander"] { border: 1px solid #21262d; border-radius: 6px; }
  .filter-card {
      background: #161b22; border: 1px solid #30363d;
      border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem;
  }
  .badge {
      display: inline-block; background: #21262d; border: 1px solid #30363d;
      border-radius: 4px; padding: 2px 8px;
      font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem;
      color: #8b949e; margin: 2px;
  }
  .section-title {
      font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem;
      letter-spacing: 0.12em; text-transform: uppercase;
      color: #58a6ff; margin-bottom: 0.5rem;
  }
  .endpoint-pill {
      display: inline-block; padding: 4px 12px; border-radius: 20px;
      font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem;
      font-weight: 600; margin-bottom: 0.5rem;
  }
  .metric-box {
      background: #161b22; border: 1px solid #30363d;
      border-radius: 8px; padding: 1rem; text-align: center;
  }
  .metric-val {
      font-family: 'IBM Plex Mono', monospace; font-size: 1.6rem;
      font-weight: 600; color: #58a6ff;
  }
  .metric-lbl { font-size: 0.8rem; color: #8b949e; margin-top: 2px; }
  .header-box {
      background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
      border-bottom: 1px solid #21262d; padding: 1.5rem 0 1rem 0; margin-bottom: 1.5rem;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-box">
  <h1 style="font-size:1.8rem; margin:0; color:#e6edf3;">
    🧮 Presupuesto Abierto — Express
  </h1>
  <p style="color:#8b949e; font-size:0.9rem; margin:4px 0 0 0; font-family:'IBM Plex Mono', monospace;">
    API v1 · presupuestoabierto.gob.ar
  </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SELECTOR DE ENDPOINT
# ─────────────────────────────────────────────
st.markdown('<p class="section-title">🔌 Tipo de consulta</p>', unsafe_allow_html=True)

tipo_consulta = st.radio(
    "Endpoint",
    options=list(ENDPOINT_CONFIG.keys()),
    format_func=lambda k: ENDPOINT_CONFIG[k]["label"],
    horizontal=True,
    label_visibility="collapsed",
)

# Resetear estado si cambia el endpoint
if st.session_state.get("last_tipo") != tipo_consulta:
    st.session_state.columnas_sel = ENDPOINT_CONFIG[tipo_consulta]["default_columns"]
    st.session_state.filters = []
    st.session_state.last_tipo = tipo_consulta

# Referencias al config activo
cfg = ENDPOINT_CONFIG[tipo_consulta]
BASE_URL = cfg["url"]
COLUMNAS_MONTO = cfg["columnas_monto"]
COLUMNAS_CLASIFICACION = cfg["columnas_clasificacion"]
COL_DEVENGADO_MENSUAL = cfg["col_devengado_mensual"]
PERMITE_INFLACION = cfg["permite_inflacion"]
TODAS_LAS_COLUMNAS = (
    [col for cols in COLUMNAS_CLASIFICACION.values() for col in cols] + COLUMNAS_MONTO
)

# Inicializar estado si no existe
if "filters" not in st.session_state:
    st.session_state.filters = []
if "columnas_sel" not in st.session_state:
    st.session_state.columnas_sel = cfg["default_columns"]


# ─────────────────────────────────────────────
# SIDEBAR — AUTH + AÑOS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="section-title">🔑 Autenticación</p>', unsafe_allow_html=True)
    st.success("API key cargada desde Secrets")

    st.markdown("---")
    st.markdown('<p class="section-title">📅 Ejercicios Presupuestarios</p>', unsafe_allow_html=True)
    anio_desde, anio_hasta = st.select_slider(
        "Rango de años",
        options=list(range(1995, 2027)),
        value=(2020, 2026),
    )
    anios_seleccionados = list(range(anio_desde, anio_hasta + 1))
    st.caption(f"{len(anios_seleccionados)} año(s) seleccionado(s)")

    st.markdown("---")
    st.markdown('<p class="section-title">⚙️ Opciones de descarga</p>', unsafe_allow_html=True)
    delay_entre_requests = st.slider(
        "Delay entre requests (seg)", 0.5, 3.0, 1.0, 0.5,
        help="Evita saturar la API con muchos requests seguidos",
    )
    nombre_archivo = st.text_input("Nombre del archivo", value="presupuesto_export")
    formato_salida = st.selectbox("Formato", ["Excel (.xlsx)", "CSV (.csv)"])

    st.markdown("---")
    if PERMITE_INFLACION:
        st.markdown('<p class="section-title">📈 Ajuste por inflación</p>', unsafe_allow_html=True)
        ajustar_inflacion = st.checkbox(
            "Agregar columnas ajustadas por inflación",
            value=False,
            help=(
                "Si la consulta no incluye mes, ajusta todas las columnas de monto por el "
                "coeficiente anual. Si incluye mes, ajusta la columna principal por el "
                "coeficiente mensual."
            ),
        )
    else:
        ajustar_inflacion = False
        st.markdown('<p class="section-title">📈 Ajuste por inflación</p>', unsafe_allow_html=True)
        st.caption("No disponible para Ejecución Física.")


# ─────────────────────────────────────────────
# COLUMNAS
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-title">📊 Columnas a consultar</p>', unsafe_allow_html=True)

with st.expander("Seleccionar columnas", expanded=True):
    col1, col2 = st.columns([2, 1])

    with col1:
        # Columnas de monto por defecto seleccionadas
        default_monto = [c for c in COLUMNAS_MONTO if c in st.session_state.columnas_sel]
        montos_sel = st.multiselect(
            f"Columnas de monto ({cfg['label']})",
            COLUMNAS_MONTO,
            default=default_monto,
            key="monto_sel",
        )

    with col2:
        # Columna año (temporal genérica)
        col_anio = (
            "impacto_presupuestario_anio"
            if tipo_consulta in ("credito", "recurso")
            else "ejercicio_presupuestario"
        )
        agregar_anio = st.checkbox(
            "Incluir año",
            value=col_anio in st.session_state.columnas_sel,
        )

    st.markdown("**Clasificación / Dimensiones:**")
    tabs = st.tabs(list(COLUMNAS_CLASIFICACION.keys()))
    dims_sel = {}
    for tab, (grupo, cols) in zip(tabs, COLUMNAS_CLASIFICACION.items()):
        with tab:
            dims_sel[grupo] = st.multiselect(
                f"Columnas de {grupo}",
                cols,
                default=[c for c in cols if c in st.session_state.columnas_sel],
                label_visibility="collapsed",
                key=f"dim_{tipo_consulta}_{grupo}",
            )

    # Consolidar selección
    columnas_finales = []
    if agregar_anio:
        columnas_finales.append(col_anio)
    for grupo_cols in dims_sel.values():
        columnas_finales.extend(grupo_cols)
    columnas_finales.extend(montos_sel)

    # Deduplicar preservando orden
    seen: set = set()
    columnas_finales = [c for c in columnas_finales if not (c in seen or seen.add(c))]

    st.session_state.columnas_sel = columnas_finales

    if columnas_finales:
        badges = " ".join(f'<span class="badge">{c}</span>' for c in columnas_finales)
        st.markdown(
            f"**{len(columnas_finales)} columna(s) seleccionada(s):**<br>{badges}",
            unsafe_allow_html=True,
        )
    else:
        st.warning("⚠️ Seleccioná al menos una columna.")


# ─────────────────────────────────────────────
# FILTROS
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-title">🔍 Filtros</p>', unsafe_allow_html=True)

if st.button("➕ Agregar filtro"):
    primera_col = TODAS_LAS_COLUMNAS[0] if TODAS_LAS_COLUMNAS else ""
    st.session_state.filters.append({
        "column": primera_col,
        "operator_label": "igual a",
        "is_between": False,
        "value": "",
        "value_from": "",
        "value_to": "",
    })

filters_to_remove = []
for i, flt in enumerate(st.session_state.filters):
    with st.container():
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        cols = st.columns([3, 2, 3, 3, 0.6])

        with cols[0]:
            col_index = (
                TODAS_LAS_COLUMNAS.index(flt["column"])
                if flt["column"] in TODAS_LAS_COLUMNAS
                else 0
            )
            flt["column"] = st.selectbox(
                "Columna", TODAS_LAS_COLUMNAS,
                index=col_index,
                key=f"fcol_{i}",
                label_visibility="collapsed",
            )

        with cols[1]:
            todas_ops = {**OPERADORES_UNO, **OPERADORES_DOS}
            op_index = (
                list(todas_ops.keys()).index(flt["operator_label"])
                if flt["operator_label"] in todas_ops
                else 0
            )
            flt["operator_label"] = st.selectbox(
                "Operador", list(todas_ops.keys()),
                index=op_index,
                key=f"fop_{i}",
                label_visibility="collapsed",
            )
            flt["is_between"] = flt["operator_label"] == "entre"

        if flt["is_between"]:
            with cols[2]:
                flt["value_from"] = st.text_input(
                    "Desde", value=flt["value_from"],
                    key=f"fvf_{i}", label_visibility="collapsed", placeholder="Desde",
                )
            with cols[3]:
                flt["value_to"] = st.text_input(
                    "Hasta", value=flt["value_to"],
                    key=f"fvt_{i}", label_visibility="collapsed", placeholder="Hasta",
                )
        else:
            with cols[2]:
                flt["value"] = st.text_input(
                    "Valor", value=flt.get("value", ""),
                    key=f"fv_{i}", label_visibility="collapsed", placeholder="Valor del filtro",
                )
            cols[3].empty()

        with cols[4]:
            if st.button("🗑", key=f"fdel_{i}", help="Eliminar filtro"):
                filters_to_remove.append(i)

        st.markdown("</div>", unsafe_allow_html=True)

for idx in reversed(filters_to_remove):
    st.session_state.filters.pop(idx)


# ─────────────────────────────────────────────
# HELPERS DE NORMALIZACIÓN
# ─────────────────────────────────────────────
def _normalizar_numero(serie: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce")
    s = (
        serie.astype(str)
        .str.strip()
        .str.replace("\u00a0", "", regex=False)
        .str.replace(" ", "", regex=False)
    )
    mascara_coma_decimal = s.str.contains(",", na=False)
    s.loc[mascara_coma_decimal] = (
        s.loc[mascara_coma_decimal]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(s, errors="coerce")


def _mes_a_numero(serie: pd.Series) -> pd.Series:
    meses = {
        "enero": 1, "ene": 1, "febrero": 2, "feb": 2,
        "marzo": 3, "mar": 3, "abril": 4, "abr": 4,
        "mayo": 5, "may": 5, "junio": 6, "jun": 6,
        "julio": 7, "jul": 7, "agosto": 8, "ago": 8,
        "septiembre": 9, "setiembre": 9, "sep": 9, "set": 9,
        "octubre": 10, "oct": 10, "noviembre": 11, "nov": 11,
        "diciembre": 12, "dic": 12,
    }
    num = pd.to_numeric(serie, errors="coerce")
    txt = (
        serie.astype(str).str.strip().str.lower()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    extraido = txt.str.extract(r"(1[0-2]|0?[1-9])", expand=False)
    num_extraido = pd.to_numeric(extraido, errors="coerce")
    por_nombre = txt.map(meses)
    return num.fillna(num_extraido).fillna(por_nombre)


# ─────────────────────────────────────────────
# CARGA DE COEFICIENTES DE INFLACIÓN
# ─────────────────────────────────────────────
@st.cache_data(ttl=60 * 60)
def cargar_ajuste_anual() -> pd.DataFrame:
    url = GOOGLE_SHEET_BASE + "Ajuste%20Inflacion"
    df = pd.read_csv(url)
    cols_lower = {str(c).strip().lower(): c for c in df.columns}
    col_anio = cols_lower.get("año") or cols_lower.get("anio")
    col_ajuste = cols_lower.get("ajuste")
    if col_anio is None or col_ajuste is None:
        raise ValueError("No se encontraron 'Año' y 'Ajuste' en la hoja 'Ajuste Inflacion'.")
    out = df[[col_anio, col_ajuste]].copy()
    out.columns = ["anio", "ajuste_inflacion"]
    out["anio"] = pd.to_numeric(out["anio"], errors="coerce").astype("Int64")
    out["ajuste_inflacion"] = _normalizar_numero(out["ajuste_inflacion"])
    return out.dropna(subset=["anio", "ajuste_inflacion"])


@st.cache_data(ttl=60 * 60)
def cargar_ajuste_mensual() -> pd.DataFrame:
    url = GOOGLE_SHEET_BASE + "IPC%20Indice"
    try:
        respuesta = requests.get(url, timeout=30)
        respuesta.raise_for_status()
    except Exception as e:
        raise ValueError(f"No se pudo leer Google Sheets para el ajuste mensual: {e}")
    if not respuesta.text.strip():
        raise ValueError("Google Sheets devolvió respuesta vacía para 'IPC Indice'.")
    try:
        df = pd.read_csv(io.StringIO(respuesta.text))
    except pd.errors.EmptyDataError:
        raise ValueError("CSV vacío desde Google Sheets para 'IPC Indice'.")
    if df.shape[1] < 8:
        raise ValueError("La hoja 'IPC Indice' debe tener al menos 8 columnas.")
    out = df.iloc[:, [0, 1, 7]].copy()
    out.columns = ["anio", "mes", "ajuste_inflacion"]
    anio_num = pd.to_numeric(out["anio"], errors="coerce")
    mes_num = _mes_a_numero(out["mes"])
    out["fecha_ajuste"] = pd.to_datetime(
        {"year": anio_num, "month": mes_num, "day": 1}, errors="coerce"
    )
    out["fecha_ajuste"] = out["fecha_ajuste"].dt.to_period("M").dt.to_timestamp()
    out["ajuste_inflacion"] = _normalizar_numero(out["ajuste_inflacion"])
    out = out.dropna(subset=["fecha_ajuste", "ajuste_inflacion"])
    if out.empty:
        raise ValueError("No se encontraron coeficientes válidos en 'IPC Indice'.")
    return out[["fecha_ajuste", "ajuste_inflacion"]].drop_duplicates(
        subset=["fecha_ajuste"], keep="last"
    )


# ─────────────────────────────────────────────
# CONSTRUCCIÓN DE PAYLOAD
# ─────────────────────────────────────────────
def construir_payload(anio: int, columnas: list, filtros: list) -> dict:
    payload = {
        "title": f"Consulta {tipo_consulta} {anio}",
        "ejercicios": [anio],
        "columns": columnas,
    }
    if filtros:
        condiciones = []
        for flt in filtros:
            if flt["is_between"]:
                condiciones.append({
                    "column": flt["column"],
                    "operator": "between",
                    "valueFrom": flt["value_from"],
                    "valueTo": flt["value_to"],
                })
            else:
                op_api = OPERADORES_UNO.get(flt["operator_label"], "equal")
                condiciones.append({
                    "column": flt["column"],
                    "operator": op_api,
                    "value": flt["value"],
                })
        payload["filters"] = condiciones
    return payload


# ─────────────────────────────────────────────
# COLUMNAS PARA CONSULTA (agrega técnicas si se ajusta inflación)
# ─────────────────────────────────────────────
def columnas_para_consulta(columnas: list) -> list:
    columnas_out = list(columnas)
    if not ajustar_inflacion:
        return columnas_out

    col_anio_key = (
        "impacto_presupuestario_anio"
        if tipo_consulta in ("credito", "recurso")
        else "ejercicio_presupuestario"
    )
    if col_anio_key not in columnas_out:
        columnas_out.insert(0, col_anio_key)

    # Si hay mes, asegurar que la columna mensual esté presente
    if "impacto_presupuestario_mes" in columnas_out and COL_DEVENGADO_MENSUAL:
        if COL_DEVENGADO_MENSUAL not in columnas_out:
            columnas_out.append(COL_DEVENGADO_MENSUAL)

    seen: set = set()
    return [c for c in columnas_out if not (c in seen or seen.add(c))]


# ─────────────────────────────────────────────
# APLICAR AJUSTE DE INFLACIÓN (genérico por endpoint)
# ─────────────────────────────────────────────
def aplicar_ajuste_inflacion(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tiene_mes = "impacto_presupuestario_mes" in df.columns

    if tiene_mes:
        if not COL_DEVENGADO_MENSUAL or COL_DEVENGADO_MENSUAL not in df.columns:
            st.warning(
                f"Para ajuste mensual se necesita la columna '{COL_DEVENGADO_MENSUAL}'. "
                "No se aplicó el ajuste."
            )
            return df

        # Construir fecha de ajuste
        if "impacto_presupuestario_fecha" in df.columns:
            df["_fecha_ajuste"] = pd.to_datetime(
                df["impacto_presupuestario_fecha"], dayfirst=True, errors="coerce"
            )
        else:
            anio_num = pd.to_numeric(df["impacto_presupuestario_anio"], errors="coerce")
            mes_num = _mes_a_numero(df["impacto_presupuestario_mes"])
            df["_fecha_ajuste"] = pd.to_datetime(
                {"year": anio_num, "month": mes_num, "day": 1}, errors="coerce"
            )
        df["_fecha_ajuste"] = df["_fecha_ajuste"].dt.to_period("M").dt.to_timestamp()

        coef = cargar_ajuste_mensual()
        df = df.merge(coef, left_on="_fecha_ajuste", right_on="fecha_ajuste", how="left")
        df[f"{COL_DEVENGADO_MENSUAL}_ajustado"] = (
            pd.to_numeric(df[COL_DEVENGADO_MENSUAL], errors="coerce") * df["ajuste_inflacion"]
        )
        df = df.drop(columns=[c for c in ["_fecha_ajuste", "fecha_ajuste"] if c in df.columns])

    else:
        col_anio_key = (
            "impacto_presupuestario_anio"
            if tipo_consulta in ("credito", "recurso")
            else "ejercicio_presupuestario"
        )
        if col_anio_key not in df.columns:
            st.warning(
                f"Para ajuste anual se necesita la columna '{col_anio_key}'. "
                "No se aplicó el ajuste."
            )
            return df

        coef = cargar_ajuste_anual()
        coef = coef.rename(columns={"anio": col_anio_key})
        df[col_anio_key] = pd.to_numeric(df[col_anio_key], errors="coerce").astype("Int64")
        df = df.merge(coef, on=col_anio_key, how="left")

        for col in [c for c in COLUMNAS_MONTO if c in df.columns]:
            df[f"{col}_ajustado"] = pd.to_numeric(df[col], errors="coerce") * df["ajuste_inflacion"]

    if "ajuste_inflacion" in df.columns and df["ajuste_inflacion"].isna().any():
        st.warning("Algunas filas no encontraron coeficiente de ajuste en Google Sheets.")

    return df


# ─────────────────────────────────────────────
# REQUEST A LA API
# ─────────────────────────────────────────────
def hacer_request(anio: int, columnas: list, filtros: list) -> tuple[pd.DataFrame | None, str | None]:
    payload = construir_payload(anio, columnas, filtros)
    url = f"{BASE_URL}?format=csv"
    headers = {
        "Authorization": PRESUPUESTO_API_KEY,
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200 and response.text.strip():
            df = pd.read_csv(io.StringIO(response.text))
            return df, None
        else:
            return None, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────
# PREVIEW DE PAYLOAD JSON
# ─────────────────────────────────────────────
st.markdown("---")
with st.expander("👁 Preview del payload JSON (primer año)", expanded=False):
    if columnas_finales:
        payload_preview = construir_payload(
            anios_seleccionados[0] if anios_seleccionados else 2025,
            columnas_para_consulta(columnas_finales),
            st.session_state.filters,
        )
        st.code(json.dumps(payload_preview, ensure_ascii=False, indent=2), language="json")
    else:
        st.info("Seleccioná columnas para ver el payload.")


# ─────────────────────────────────────────────
# BOTONES DE ACCIÓN
# ─────────────────────────────────────────────
st.markdown("---")
col_btn1, col_btn2, _ = st.columns([2, 1, 1])

api_key = PRESUPUESTO_API_KEY
can_run = bool(columnas_finales and api_key)

with col_btn1:
    iniciar = st.button(
        "🚀 Ejecutar consulta y descargar",
        disabled=not can_run,
        use_container_width=True,
        type="primary",
    )
with col_btn2:
    preview_btn = st.button(
        "👁 Preview (1er año)",
        disabled=not can_run,
        use_container_width=True,
    )


# ─────────────────────────────────────────────
# PREVIEW RÁPIDO (1 año)
# ─────────────────────────────────────────────
if preview_btn and columnas_finales:
    primer_anio = anios_seleccionados[0] if anios_seleccionados else 2025
    with st.spinner(f"Consultando {cfg['label']} · año {primer_anio}…"):
        cols_req = columnas_para_consulta(columnas_finales)
        df_prev, err = hacer_request(primer_anio, cols_req, st.session_state.filters)
        if ajustar_inflacion and df_prev is not None and not df_prev.empty:
            try:
                df_prev = aplicar_ajuste_inflacion(df_prev)
            except Exception as e:
                st.error(f"No se pudo aplicar el ajuste: {e}")

    if err:
        st.error(f"Error: {err}")
    elif df_prev is not None and not df_prev.empty:
        st.success(f"✅ {len(df_prev):,} filas · {len(df_prev.columns)} columnas")
        st.dataframe(df_prev.head(50), use_container_width=True)
    else:
        st.warning("Sin resultados para ese año con los filtros aplicados.")


# ─────────────────────────────────────────────
# DESCARGA COMPLETA (todos los años)
# ─────────────────────────────────────────────
if iniciar and columnas_finales:
    dataframes = []
    errores = []
    total = len(anios_seleccionados)

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, anio in enumerate(anios_seleccionados):
        status_text.markdown(
            f"⏳ Descargando **{cfg['label']}** · **{anio}** ({idx + 1}/{total})…"
        )
        cols_req = columnas_para_consulta(columnas_finales)
        df_anio, err = hacer_request(anio, cols_req, st.session_state.filters)

        if df_anio is not None and not df_anio.empty:
            dataframes.append(df_anio)
        elif err:
            errores.append(f"Año {anio}: {err}")

        progress_bar.progress((idx + 1) / total)
        if idx < total - 1:
            time.sleep(delay_entre_requests)

    status_text.empty()
    progress_bar.empty()

    if dataframes:
        df_total = pd.concat(dataframes, ignore_index=True)

        if ajustar_inflacion:
            try:
                df_total = aplicar_ajuste_inflacion(df_total)
            except Exception as e:
                st.error(f"No se pudo aplicar el ajuste por inflación: {e}")

        # ── Métricas resumen ──
        c1, c2, c3, c4 = st.columns(4)
        metricas = [
            (c1, f"{len(df_total):,}", "Filas totales"),
            (c2, f"{len(dataframes)}", "Años con datos"),
            (c3, f"{len(df_total.columns)}", "Columnas"),
        ]
        cols_monto_pres = [c for c in COLUMNAS_MONTO if c in df_total.columns]
        if cols_monto_pres:
            val = pd.to_numeric(df_total[cols_monto_pres[0]], errors="coerce").sum()
            label = cols_monto_pres[0].replace("_", " ").title()
            metricas.append((c4, f"${val / 1e9:.1f}B", label))
        else:
            metricas.append((c4, "-", "Sin monto"))

        for col, val, lbl in metricas:
            col.markdown(
                f"""<div class="metric-box">
                  <div class="metric-val">{val}</div>
                  <div class="metric-lbl">{lbl}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df_total.head(100), use_container_width=True)

        # ── Descarga ──
        nombre_final = nombre_archivo.replace(" ", "_")
        if "Excel" in formato_salida:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df_total.to_excel(writer, index=False, sheet_name="Presupuesto")
            buf.seek(0)
            st.download_button(
                label="⬇️ Descargar Excel",
                data=buf,
                file_name=f"{nombre_final}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary",
            )
        else:
            csv_data = df_total.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Descargar CSV",
                data=csv_data,
                file_name=f"{nombre_final}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary",
            )

        if errores:
            with st.expander(f"⚠️ {len(errores)} errores al descargar"):
                for e in errores:
                    st.text(e)
    else:
        st.error("No se obtuvieron datos. Revisá los filtros o el rango de años.")
        for e in errores:
            st.text(e)
