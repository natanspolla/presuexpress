import streamlit as st
import requests
import pandas as pd
import io
import json
import time
from itertools import product

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Presupuesto Abierto — Consultor",
    page_icon="🏛️",
    layout="wide",
)

# ─────────────────────────────────────────────
# ACCESO PRIVADO + SECRETS STREAMLIT CLOUD
# ─────────────────────────────────────────────
def get_secret(name: str, default: str = "") -> str:
    """Lee secretos de Streamlit Cloud sin romper la app si todavía no están configurados."""
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

APP_ACCESS_CODE = get_secret("APP_ACCESS_CODE")
PRESUPUESTO_API_KEY = get_secret("PRESUPUESTO_API_KEY")

if not APP_ACCESS_CODE or not PRESUPUESTO_API_KEY:
    st.error("Faltan configurar secrets en Streamlit Cloud. Agregá APP_ACCESS_CODE y PRESUPUESTO_API_KEY en Settings → Secrets.")
    st.stop()

codigo_ingresado = st.text_input("Código de acceso", type="password")
if codigo_ingresado != APP_ACCESS_CODE:
    st.warning("Ingresá el código de acceso para usar la app.")
    st.stop()

BASE_URL = "https://www.presupuestoabierto.gob.ar/api/v1/credito"
GOOGLE_SHEET_ID = "1vT5nCBy1lbh4KNxmQhxclhkHsGiO5qB_m0PkyaWtlrs"
GOOGLE_SHEET_BASE = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet="

# ─────────────────────────────────────────────
# DEFINICIÓN DE COLUMNAS (del schema)
# ─────────────────────────────────────────────
COLUMNAS_CREDITO = [
    "credito_presupuestado",
    "credito_vigente",
    "credito_comprometido",
    "credito_devengado",
    "credito_pagado",
]

COLUMNAS_CLASIFICACION = {
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
}

TODAS_LAS_COLUMNAS = [col for cols in COLUMNAS_CLASIFICACION.values() for col in cols] + COLUMNAS_CREDITO

OPERADORES_UNO = {
    "igual a": "equal",
    "contiene (like)": "like",
    "mayor que": "greater_than",
    "mayor o igual que": "greater_equal_than",
    "menor que": "lower_than",
    "menor o igual que": "lower_equal_than",
}

OPERADORES_DOS = {
    "entre": "between",
}


# ─────────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

  html, body, [class*="css"] {
      font-family: 'IBM Plex Sans', sans-serif;
  }
  .main { background: #0d1117; }
  h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; }

  .stButton > button {
      background: #58a6ff;
      color: #0d1117;
      font-family: 'IBM Plex Mono', monospace;
      font-weight: 600;
      border: none;
      border-radius: 4px;
      padding: 0.5rem 1.5rem;
  }
  .stButton > button:hover {
      background: #79c0ff;
  }

  div[data-testid="stExpander"] {
      border: 1px solid #21262d;
      border-radius: 6px;
  }

  .filter-card {
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 0.75rem;
  }
  .badge {
      display: inline-block;
      background: #21262d;
      border: 1px solid #30363d;
      border-radius: 4px;
      padding: 2px 8px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 0.75rem;
      color: #8b949e;
      margin: 2px;
  }
  .section-title {
      font-family: 'IBM Plex Mono', monospace;
      font-size: 0.7rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #58a6ff;
      margin-bottom: 0.5rem;
  }
  .json-preview {
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 6px;
      padding: 1rem;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 0.78rem;
      color: #e6edf3;
      max-height: 320px;
      overflow-y: auto;
  }
  .metric-box {
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 8px;
      padding: 1rem;
      text-align: center;
  }
  .metric-val {
      font-family: 'IBM Plex Mono', monospace;
      font-size: 1.6rem;
      font-weight: 600;
      color: #58a6ff;
  }
  .metric-lbl {
      font-size: 0.8rem;
      color: #8b949e;
      margin-top: 2px;
  }
  .header-box {
      background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
      border-bottom: 1px solid #21262d;
      padding: 1.5rem 0 1rem 0;
      margin-bottom: 1.5rem;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-box">
  <h1 style="font-size:1.8rem; margin:0; color:#e6edf3;">
    🏛️ Presupuesto Abierto — Consultor
  </h1>
  <p style="color:#8b949e; font-size:0.9rem; margin:4px 0 0 0; font-family:'IBM Plex Mono', monospace;">
    API v1 · presupuestoabierto.gob.ar
  </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INICIALIZAR STATE
# ─────────────────────────────────────────────
if "filters" not in st.session_state:
    st.session_state.filters = []
if "columnas_sel" not in st.session_state:
    st.session_state.columnas_sel = [
        "impacto_presupuestario_anio",
        "jurisdiccion_desc",
        "programa_desc",
        "actividad_desc",
        "credito_presupuestado",
        "credito_vigente",
        "credito_devengado",
    ]


# ─────────────────────────────────────────────
# SIDEBAR — AUTH + AÑOS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="section-title">🔑 Autenticación</p>', unsafe_allow_html=True)
    api_key = PRESUPUESTO_API_KEY
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
    st.markdown('<p class="section-title">📈 Ajuste por inflación</p>', unsafe_allow_html=True)
    ajustar_inflacion = st.checkbox(
        "Agregar columnas ajustadas por inflación",
        value=False,
        help=(
            "Si la consulta no incluye mes, ajusta todas las columnas de crédito por el coeficiente anual. "
            "Si incluye mes, ajusta solo credito_devengado por el coeficiente mensual."
        ),
    )


# ─────────────────────────────────────────────
# COLUMNAS
# ─────────────────────────────────────────────
st.markdown('<p class="section-title">📊 Columnas a consultar</p>', unsafe_allow_html=True)

with st.expander("Seleccionar columnas", expanded=True):
    # Selector rápido de columnas de crédito
    col1, col2 = st.columns([2, 1])
    with col1:
        creditos_sel = st.multiselect(
            "Columnas de crédito $",
            COLUMNAS_CREDITO,
            default=[c for c in ["credito_presupuestado", "credito_vigente", "credito_devengado"]
                     if c in st.session_state.columnas_sel],
            key="cred_sel",
        )

    with col2:
        agregar_anio = st.checkbox(
            "Incluir año", value="impacto_presupuestario_anio" in st.session_state.columnas_sel
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
                key=f"dim_{grupo}",
            )

    # Consolidar selección
    columnas_finales = []
    if agregar_anio:
        columnas_finales.append("impacto_presupuestario_anio")
    for grupo_cols in dims_sel.values():
        columnas_finales.extend(grupo_cols)
    columnas_finales.extend(creditos_sel)
    # Deduplicar preservando orden
    seen = set()
    columnas_finales = [c for c in columnas_finales if not (c in seen or seen.add(c))]

    st.session_state.columnas_sel = columnas_finales

    if columnas_finales:
        badges = " ".join(f'<span class="badge">{c}</span>' for c in columnas_finales)
        st.markdown(f"**{len(columnas_finales)} columna(s) seleccionada(s):**<br>{badges}", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Seleccioná al menos una columna.")


# ─────────────────────────────────────────────
# FILTROS
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-title">🔍 Filtros</p>', unsafe_allow_html=True)

# Botón para agregar filtro
if st.button("➕ Agregar filtro"):
    st.session_state.filters.append({
        "column": "programa_desc",
        "operator_label": "contiene (like)",
        "is_between": False,
        "value": "",
        "value_from": "",
        "value_to": "",
    })

# Renderizar filtros existentes
filters_to_remove = []
for i, flt in enumerate(st.session_state.filters):
    with st.container():
        st.markdown(f'<div class="filter-card">', unsafe_allow_html=True)
        cols = st.columns([3, 2, 3, 3, 0.6])

        with cols[0]:
            flt["column"] = st.selectbox(
                "Columna",
                TODAS_LAS_COLUMNAS,
                index=TODAS_LAS_COLUMNAS.index(flt["column"]) if flt["column"] in TODAS_LAS_COLUMNAS else 0,
                key=f"fcol_{i}",
                label_visibility="collapsed",
            )

        with cols[1]:
            todas_ops = {**OPERADORES_UNO, **OPERADORES_DOS}
            flt["operator_label"] = st.selectbox(
                "Operador",
                list(todas_ops.keys()),
                index=list(todas_ops.keys()).index(flt["operator_label"])
                if flt["operator_label"] in todas_ops else 0,
                key=f"fop_{i}",
                label_visibility="collapsed",
            )
            flt["is_between"] = flt["operator_label"] == "entre"

        if flt["is_between"]:
            with cols[2]:
                flt["value_from"] = st.text_input("Desde", value=flt["value_from"], key=f"fvf_{i}", label_visibility="collapsed", placeholder="Desde")
            with cols[3]:
                flt["value_to"] = st.text_input("Hasta", value=flt["value_to"], key=f"fvt_{i}", label_visibility="collapsed", placeholder="Hasta")
        else:
            with cols[2]:
                flt["value"] = st.text_input("Valor", value=flt.get("value", ""), key=f"fv_{i}", label_visibility="collapsed", placeholder="Valor del filtro")
            cols[3].empty()

        with cols[4]:
            if st.button("🗑", key=f"fdel_{i}", help="Eliminar filtro"):
                filters_to_remove.append(i)

        st.markdown("</div>", unsafe_allow_html=True)

for idx in reversed(filters_to_remove):
    st.session_state.filters.pop(idx)


# ─────────────────────────────────────────────
# PREVIEW DEL PAYLOAD JSON
# ─────────────────────────────────────────────
st.markdown("---")

def construir_payload(anio: int, columnas: list, filtros: list) -> dict:
    payload = {
        "title": f"Consulta presupuestaria {anio}",
        "ejercicios": [anio],
        "columns": columnas,
    }
    if filtros:
        condiciones = []
        for flt in filtros:
            op_label = flt["operator_label"]
            if flt["is_between"]:
                condiciones.append({
                    "column": flt["column"],
                    "operator": "between",
                    "valueFrom": flt["value_from"],
                    "valueTo": flt["value_to"],
                })
            else:
                op_api = OPERADORES_UNO.get(op_label, "equal")
                condiciones.append({
                    "column": flt["column"],
                    "operator": op_api,
                    "value": flt["value"],
                })
        payload["filters"] = condiciones
    return payload


with st.expander("👁 Preview del payload JSON (primer año)", expanded=False):
    if columnas_finales:
        payload_preview = construir_payload(
            anios_seleccionados[0] if anios_seleccionados else 2025,
            columnas_finales,
            st.session_state.filters,
        )
        st.code(json.dumps(payload_preview, ensure_ascii=False, indent=2), language="json")
    else:
        st.info("Seleccioná columnas para ver el payload.")


# ─────────────────────────────────────────────
# DESCARGA
# ─────────────────────────────────────────────
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

with col_btn1:
    iniciar = st.button(
        "🚀 Ejecutar consulta y descargar",
        disabled=not columnas_finales or not api_key,
        use_container_width=True,
        type="primary",
    )

with col_btn2:
    # Preview rápido (solo primer año)
    preview_btn = st.button(
        "👁 Preview (1er año)",
        disabled=not columnas_finales or not api_key,
        use_container_width=True,
    )


def _normalizar_numero(serie: pd.Series) -> pd.Series:
    """Convierte números provenientes de Google Sheets, tolerando coma decimal y separadores."""
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce")

    s = (
        serie.astype(str)
        .str.strip()
        .str.replace("\u00a0", "", regex=False)
        .str.replace(" ", "", regex=False)
    )

    # Caso habitual AR: 1.234,56 -> 1234.56
    mascara_coma_decimal = s.str.contains(",", na=False)
    s.loc[mascara_coma_decimal] = (
        s.loc[mascara_coma_decimal]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    return pd.to_numeric(s, errors="coerce")



def _mes_a_numero(serie: pd.Series) -> pd.Series:
    """Convierte mes de la API/Sheets a número: acepta 1, 01, Enero, ene, 1 - Enero, etc."""
    meses = {
        "enero": 1, "ene": 1,
        "febrero": 2, "feb": 2,
        "marzo": 3, "mar": 3,
        "abril": 4, "abr": 4,
        "mayo": 5, "may": 5,
        "junio": 6, "jun": 6,
        "julio": 7, "jul": 7,
        "agosto": 8, "ago": 8,
        "septiembre": 9, "setiembre": 9, "sep": 9, "set": 9,
        "octubre": 10, "oct": 10,
        "noviembre": 11, "nov": 11,
        "diciembre": 12, "dic": 12,
    }

    num = pd.to_numeric(serie, errors="coerce")
    txt = serie.astype(str).str.strip().str.lower()
    txt = txt.str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("utf-8")
    extraido = txt.str.extract(r"(1[0-2]|0?[1-9])", expand=False)
    num_extraido = pd.to_numeric(extraido, errors="coerce")
    por_nombre = txt.map(meses)
    return num.fillna(num_extraido).fillna(por_nombre)
@st.cache_data(ttl=60 * 60)
def cargar_ajuste_anual() -> pd.DataFrame:
    url = GOOGLE_SHEET_BASE + "Ajuste%20Inflacion"
    df = pd.read_csv(url)

    # La hoja tiene: B = Año, C = IPC promedio, D = Inflación promedio interanual, E = Ajuste.
    # Se buscan por nombre para que funcione aunque Google Sheets exporte también una columna A vacía.
    cols_lower = {str(c).strip().lower(): c for c in df.columns}

    col_anio = cols_lower.get("año") or cols_lower.get("anio")
    col_ajuste = cols_lower.get("ajuste")

    if col_anio is None or col_ajuste is None:
        raise ValueError("No se encontraron las columnas 'Año' y 'Ajuste' en la hoja 'Ajuste Inflacion'.")

    out = df[[col_anio, col_ajuste]].copy()
    out.columns = ["impacto_presupuestario_anio", "ajuste_inflacion"]
    out["impacto_presupuestario_anio"] = pd.to_numeric(out["impacto_presupuestario_anio"], errors="coerce").astype("Int64")
    out["ajuste_inflacion"] = _normalizar_numero(out["ajuste_inflacion"])
    out = out.dropna(subset=["impacto_presupuestario_anio", "ajuste_inflacion"])
    return out


@st.cache_data(ttl=60 * 60)
def cargar_ajuste_mensual() -> pd.DataFrame:
    # Hoja IPC Indice con formato:
    # A = Año, B = Mes, C = Fecha, D = IPC, E = Var. mensual,
    # F = Var. mensual + REM, G = Var. anual, H = Ajuste al último mes.
    # Se toman las columnas por posición para no depender del nombre exacto
    # de la columna H, que puede cambiar según el último mes disponible.
    url = GOOGLE_SHEET_BASE + "IPC%20Indice"

    try:
        respuesta = requests.get(url, timeout=30)
        respuesta.raise_for_status()
    except Exception as e:
        raise ValueError(f"No se pudo leer Google Sheets para el ajuste mensual: {e}")

    if not respuesta.text.strip():
        raise ValueError(
            "Google Sheets devolvió una respuesta vacía. Verificá que el archivo esté compartido "
            "como 'cualquier persona con el enlace puede ver' y que exista la hoja 'IPC Indice'."
        )

    try:
        df = pd.read_csv(io.StringIO(respuesta.text))
    except pd.errors.EmptyDataError:
        raise ValueError("No se pudieron leer datos desde Google Sheets. La respuesta CSV llegó vacía.")

    if df.shape[1] < 8:
        raise ValueError(
            "La hoja 'IPC Indice' debe tener al menos 8 columnas: "
            "A=Año, B=Mes, C=Fecha y H=Ajuste al último mes."
        )

    out = df.iloc[:, [0, 1, 2, 7]].copy()
    out.columns = ["anio", "mes", "fecha", "ajuste_inflacion"]

    anio_num = pd.to_numeric(out["anio"], errors="coerce")
    mes_num = _mes_a_numero(out["mes"])

    # La fecha de la hoja puede venir como jun/2006; para evitar ambigüedades,
    # el match principal se construye con Año + Mes + día 1.
    out["fecha_ajuste"] = pd.to_datetime(
        {"year": anio_num, "month": mes_num, "day": 1},
        errors="coerce",
    )
    out["fecha_ajuste"] = out["fecha_ajuste"].dt.to_period("M").dt.to_timestamp()
    out["ajuste_inflacion"] = _normalizar_numero(out["ajuste_inflacion"])
    out = out.dropna(subset=["fecha_ajuste", "ajuste_inflacion"])

    if out.empty:
        raise ValueError(
            "No se encontraron coeficientes válidos en 'IPC Indice'. "
            "Revisá que A sea Año, B sea Mes y H sea Ajuste al último mes."
        )

    return out[["fecha_ajuste", "ajuste_inflacion"]].drop_duplicates(subset=["fecha_ajuste"], keep="last")


def columnas_para_consulta(columnas: list, ajustar_inflacion: bool) -> list:
    """Agrega columnas técnicas necesarias para calcular el ajuste, si el usuario no las seleccionó."""
    columnas_out = list(columnas)

    if not ajustar_inflacion:
        return columnas_out

    if "impacto_presupuestario_anio" not in columnas_out:
        columnas_out.insert(0, "impacto_presupuestario_anio")

    if "impacto_presupuestario_mes" in columnas_out:
        if "credito_devengado" not in columnas_out:
            columnas_out.append("credito_devengado")

    seen = set()
    return [c for c in columnas_out if not (c in seen or seen.add(c))]


def aplicar_ajuste_inflacion(df: pd.DataFrame, columnas_usuario: list) -> pd.DataFrame:
    """Agrega columnas de crédito ajustadas por inflación según el nivel temporal de la consulta."""
    df = df.copy()

    tiene_mes = "impacto_presupuestario_mes" in df.columns

    if tiene_mes:
        if "credito_devengado" not in df.columns:
            st.warning("Para ajuste mensual se necesita la columna credito_devengado. No se aplicó el ajuste.")
            return df

        if "impacto_presupuestario_fecha" in df.columns:
            df["_fecha_ajuste"] = pd.to_datetime(df["impacto_presupuestario_fecha"], dayfirst=True, errors="coerce")
        elif {"impacto_presupuestario_anio", "impacto_presupuestario_mes"}.issubset(df.columns):
            # La API no siempre trae impacto_presupuestario_fecha.
            # Por eso se construye una fecha tecnica: anio + mes + dia 1.
            anio = pd.to_numeric(df["impacto_presupuestario_anio"], errors="coerce")
            mes = _mes_a_numero(df["impacto_presupuestario_mes"])
            df["_fecha_ajuste"] = pd.to_datetime(
                {"year": anio, "month": mes, "day": 1},
                errors="coerce",
            )
        else:
            st.warning("Para ajuste mensual se necesita año y mes. No se aplicó el ajuste.")
            return df

        df["_fecha_ajuste"] = df["_fecha_ajuste"].dt.to_period("M").dt.to_timestamp()
        coef = cargar_ajuste_mensual()
        df = df.merge(coef, left_on="_fecha_ajuste", right_on="fecha_ajuste", how="left")
        df["credito_devengado_ajustado"] = pd.to_numeric(df["credito_devengado"], errors="coerce") * df["ajuste_inflacion"]
        df = df.drop(columns=[c for c in ["_fecha_ajuste", "fecha_ajuste"] if c in df.columns])

    else:
        if "impacto_presupuestario_anio" not in df.columns:
            st.warning("Para ajuste anual se necesita la columna impacto_presupuestario_anio. No se aplicó el ajuste.")
            return df

        coef = cargar_ajuste_anual()
        df["impacto_presupuestario_anio"] = pd.to_numeric(df["impacto_presupuestario_anio"], errors="coerce").astype("Int64")
        df = df.merge(coef, on="impacto_presupuestario_anio", how="left")

        cols_credito = [c for c in COLUMNAS_CREDITO if c in df.columns]
        for col in cols_credito:
            df[f"{col}_ajustado"] = pd.to_numeric(df[col], errors="coerce") * df["ajuste_inflacion"]

    # Si el año fue agregado solo como columna técnica, se conserva porque permite auditar el coeficiente.
    if df["ajuste_inflacion"].isna().any():
        st.warning("Algunas filas no encontraron coeficiente de ajuste en Google Sheets.")

    return df


def hacer_request(anio, columnas, filtros, api_key):
    payload = construir_payload(anio, columnas, filtros)
    url = f"{BASE_URL}?format=csv"
    headers = {
        "Authorization": api_key,
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


# Preview rápido
if preview_btn and columnas_finales:
    with st.spinner(f"Consultando año {anios_seleccionados[0]}…"):
        columnas_consulta = columnas_para_consulta(columnas_finales, ajustar_inflacion)
        df_prev, err = hacer_request(
            anios_seleccionados[0], columnas_consulta,
            st.session_state.filters, api_key
        )
        if ajustar_inflacion and df_prev is not None and not df_prev.empty:
            df_prev = aplicar_ajuste_inflacion(df_prev, columnas_finales)
    if err:
        st.error(f"Error: {err}")
    elif df_prev is not None and not df_prev.empty:
        st.success(f"✅ {len(df_prev):,} filas · {len(df_prev.columns)} columnas")
        st.dataframe(df_prev.head(50), use_container_width=True)
    else:
        st.warning("Sin resultados para ese año con los filtros aplicados.")


# Descarga completa
if iniciar and columnas_finales:
    dataframes = []
    errores = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    total = len(anios_seleccionados)
    for idx, anio in enumerate(anios_seleccionados):
        status_text.markdown(f"⏳ Descargando **{anio}** ({idx+1}/{total})…")
        columnas_consulta = columnas_para_consulta(columnas_finales, ajustar_inflacion)
        df_anio, err = hacer_request(anio, columnas_consulta, st.session_state.filters, api_key)

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
                df_total = aplicar_ajuste_inflacion(df_total, columnas_finales)
            except Exception as e:
                st.error(f"No se pudo aplicar el ajuste por inflación: {e}")

        # Métricas resumen
        c1, c2, c3, c4 = st.columns(4)
        metricas = [
            (c1, f"{len(df_total):,}", "Filas totales"),
            (c2, f"{len(dataframes)}", "Años con datos"),
            (c3, f"{len(df_total.columns)}", "Columnas"),
        ]
        cols_credito_pres = [c for c in COLUMNAS_CREDITO if c in df_total.columns]
        if cols_credito_pres:
            val = df_total[cols_credito_pres[0]].sum()
            metricas.append((c4, f"${val/1e9:.1f}B", cols_credito_pres[0].replace("_", " ").title()))
        else:
            metricas.append((c4, "-", "Sin crédito"))

        for col, val, lbl in metricas:
            col.markdown(f"""
            <div class="metric-box">
              <div class="metric-val">{val}</div>
              <div class="metric-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df_total.head(100), use_container_width=True)

        # Preparar descarga
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
