"""
╔══════════════════════════════════════════════════════════╗
║   PORLLES — Dashboard Ejecutivo de Leads WhatsApp        ║
║   Fuente: Whaticket conversations report                  ║
║   Ejecutar: streamlit run dashboard.py                    ║
╚══════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import re
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Porlles · Dashboard Leads",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS GLOBALES
# ─────────────────────────────────────────────

st.markdown("""
<style>
    /* Fuente y fondo general */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Ocultar menú hamburguesa y footer de Streamlit */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    /* Ocultamos el header sin afectar el botón de sidebar */
    header { visibility: hidden; height: 0 !important; min-height: 0 !important; }

    /* Botón toggle del sidebar — siempre visible y accesible */
    section[data-testid="collapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        position: fixed !important;
        top: 0.4rem !important;
        left: 0.4rem !important;
        z-index: 999999 !important;
        background: #0f172a !important;
        border-radius: 6px !important;
        padding: 2px !important;
    }
    section[data-testid="collapsedControl"] button,
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button {
        visibility: visible !important;
        color: #cbd5e1 !important;
    }

    /* Sidebar limpio */
    [data-testid="stSidebar"] {
        background: #0f172a;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label { color: #94a3b8 !important; }

    /* Título sidebar */
    .sidebar-title {
        font-size: 18px;
        font-weight: 700;
        color: #f8fafc !important;
        padding: 8px 0 4px;
        letter-spacing: -0.3px;
    }
    .sidebar-sub {
        font-size: 12px;
        color: #64748b !important;
        margin-bottom: 20px;
    }

    /* Métricas personalizadas */
    .metric-block {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 0;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 500;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #0f172a;
        line-height: 1;
        margin-bottom: 4px;
    }
    .metric-delta-pos {
        font-size: 12px;
        color: #16a34a;
        font-weight: 500;
    }
    .metric-delta-neg {
        font-size: 12px;
        color: #dc2626;
        font-weight: 500;
    }
    .metric-delta-neutral {
        font-size: 12px;
        color: #64748b;
    }

    /* Sección header */
    .section-header {
        font-size: 13px;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 20px 0 10px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 16px;
    }

    /* Alert boxes */
    .alert-danger {
        background: #fef2f2;
        border-left: 3px solid #ef4444;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 13px;
        color: #7f1d1d;
    }
    .alert-warning {
        background: #fffbeb;
        border-left: 3px solid #f59e0b;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 13px;
        color: #78350f;
    }
    .alert-success {
        background: #f0fdf4;
        border-left: 3px solid #22c55e;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 13px;
        color: #14532d;
    }
    .alert-info {
        background: #eff6ff;
        border-left: 3px solid #3b82f6;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 13px;
        color: #1e3a8a;
    }

    /* Tabla de agentes */
    .agent-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .agent-table th {
        background: #f8fafc;
        color: #475569;
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 10px 12px;
        text-align: left;
        border-bottom: 1px solid #e2e8f0;
    }
    .agent-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #f1f5f9;
        color: #334155;
        vertical-align: middle;
    }
    .agent-table tr:last-child td { border-bottom: none; }
    .agent-table tr:hover td { background: #f8fafc; }

    /* Badge */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-green { background: #dcfce7; color: #166534; }
    .badge-red   { background: #fee2e2; color: #991b1b; }
    .badge-amber { background: #fef9c3; color: #854d0e; }
    .badge-blue  { background: #dbeafe; color: #1e40af; }
    .badge-gray  { background: #f1f5f9; color: #475569; }

    /* Barra de progreso de funnel */
    .funnel-bar-bg {
        background: #f1f5f9;
        border-radius: 4px;
        height: 22px;
        position: relative;
        overflow: hidden;
    }
    .funnel-bar-fill {
        height: 100%;
        border-radius: 4px;
        display: flex;
        align-items: center;
        padding-left: 8px;
        font-size: 11px;
        font-weight: 600;
        color: #fff;
        transition: width 0.3s ease;
    }

    /* Card contenedor */
    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
    }

    /* Tag pill */
    .tag-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        background: #f1f5f9;
        color: #334155;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def hms_to_hours(val):
    """Convierte HH:MM:SS a horas decimales."""
    if pd.isna(val) or str(val).strip() == "":
        return None
    parts = str(val).strip().split(":")
    try:
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
        return round(h + m / 60 + s / 3600, 2)
    except:
        return None


def normalizar_numero(val):
    """Limpia número peruano a 9 dígitos."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    try:
        s = str(int(float(s)))
    except:
        pass
    digits = re.sub(r"\D", "", s)
    if digits.startswith("51") and len(digits) == 11:
        digits = digits[2:]
    if len(digits) == 9 and digits.startswith("9"):
        return digits
    return None


def metric_card(label, value, delta=None, delta_type="neutral"):
    delta_html = ""
    if delta:
        cls = f"metric-delta-{delta_type}"
        icon = "▲" if delta_type == "pos" else ("▼" if delta_type == "neg" else "●")
        delta_html = f'<div class="{cls}">{icon} {delta}</div>'
    return f"""
    <div class="metric-block">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """


PALETA = {
    "CHELSEA":  "#7c3aed",
    "KATIUSKA": "#0ea5e9",
    "KARINA":   "#f97316",
}

FUNNEL_ORDEN = [
    "BIENVENIDO API",
    "PRIMER FILTRO",
    "INTERESADO-SEGUIMIENTO ⏳ porlles",
    "MALA CALIDAD porlles",
    "ZONA HOT 🔥",
    "COMPRARON CON NOSOTROS 🏆",
    "BASURA",
    "CLIENTE FUTURO",
]

FUNNEL_LABELS = {
    "BIENVENIDO API":                          "Bienvenido API (chatbot)",
    "PRIMER FILTRO":                           "Primer filtro",
    "INTERESADO-SEGUIMIENTO ⏳ porlles":       "Interesado / seguimiento",
    "MALA CALIDAD porlles":                    "Mala calidad (precio)",
    "ZONA HOT 🔥":                             "Zona Hot 🔥",
    "COMPRARON CON NOSOTROS 🏆":               "Compraron con nosotros ✓",
    "BASURA":                                  "Basura / ruido",
    "CLIENTE FUTURO":                          "Cliente futuro",
}

FUNNEL_COLORES = {
    "BIENVENIDO API":                         "#94a3b8",
    "PRIMER FILTRO":                          "#3b82f6",
    "INTERESADO-SEGUIMIENTO ⏳ porlles":      "#10b981",
    "MALA CALIDAD porlles":                   "#f59e0b",
    "ZONA HOT 🔥":                            "#ef4444",
    "COMPRARON CON NOSOTROS 🏆":              "#16a34a",
    "BASURA":                                 "#cbd5e1",
    "CLIENTE FUTURO":                         "#a78bfa",
}

DOW_ES = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}
DOW_ORDEN = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


# ─────────────────────────────────────────────
# CARGA Y PROCESAMIENTO DE DATOS
# ─────────────────────────────────────────────

@st.cache_data(show_spinner="Cargando datos...")
def cargar_datos(archivo):
    df = pd.read_excel(archivo, sheet_name="Report")

    # Fechas
    for col in ["createdAt", "firstSentMessageAt", "resolvedAt", "assignedAt"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Tiempos
    df["resp_h"]   = df["workingHoursResponseTime"].apply(hms_to_hours)
    df["resol_h"]  = df["workingHoursResolutionTime"].apply(hms_to_hours)

    # Fecha derivadas
    df["fecha"]    = df["createdAt"].dt.date
    df["hora"]     = df["createdAt"].dt.hour
    df["dow_en"]   = df["createdAt"].dt.day_name()
    df["dow_es"]   = df["dow_en"].map(DOW_ES)
    df["semana"]   = df["createdAt"].dt.isocalendar().week.astype(int)

    # Número normalizado
    df["celular_norm"] = df["contactNumber"].apply(normalizar_numero)

    # Tags separados
    def extract_tags(tags):
        if pd.isna(tags):
            return []
        return [t.strip() for t in str(tags).split(",") if t.strip()]

    df["tags_list"] = df["tags"].apply(extract_tags)

    # Asesora destino desde tags
    asesoras = ["KARINA", "JOSELYN", "MARYORY", "ROMINA", "JULIO",
                "SOFIA", "DAMARIS", "HILARY", "GABRIELA", "KAROL"]
    def asesora_destino(tags):
        if pd.isna(tags):
            return "Sin asignar"
        tu = tags.upper()
        for a in asesoras:
            if a in tu:
                return a
        return "Sin asignar"

    df["asesora_destino"] = df["tags"].apply(asesora_destino)

    # Flags de tags
    df["es_cotizando"] = df["tags"].astype(str).str.lower().str.contains("cotizando")
    df["es_nca"]       = df["tags"].astype(str).str.upper().str.contains("NCA")
    df["es_redes"]     = df["tags"].astype(str).str.upper().str.contains("REDES SOCIALES")

    # Normalizar departamento vacío
    df["department"] = df["department"].fillna("Sin departamento")

    # Nombre corto del agente (PAMELA - 932471545 → KARINA)
    df["agente_corto"] = df["user"].str.replace(" - 932471545", "", regex=False)
    df["agente_corto"] = df["agente_corto"].replace({"PAMELA": "KARINA"})

    # Etapa simplificada para embudo
    etapa_map = {
        "COMPRARON CON NOSOTROS 🏆":          "Compra",
        "ZONA HOT 🔥":                         "Zona Hot",
        "INTERESADO-SEGUIMIENTO ⏳ porlles":   "Interesado",
        "PRIMER FILTRO":                       "Primer filtro",
        "BIENVENIDO API":                      "Bot / API",
        "MALA CALIDAD porlles":               "Mala calidad",
        "BASURA":                              "Basura",
        "CLIENTE FUTURO":                      "Cliente futuro",
    }
    df["etapa"] = df["department"].map(etapa_map).fillna(df["department"])

    return df


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sidebar-title">💻 Porlles</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Dashboard ejecutivo · Leads WhatsApp</div>', unsafe_allow_html=True)

    archivo = st.file_uploader(
        "Subir reporte Whaticket (.xlsx)",
        type=["xlsx"],
        help="Exportar desde Whaticket → Reportes → Conversaciones",
    )

    if archivo is None:
        st.info("Sube el archivo Excel de Whaticket para comenzar.")
    else:
        df = cargar_datos(archivo)

        st.markdown("---")
        st.markdown("**Filtros**")

        # Rango de fechas
        fecha_min = df["createdAt"].min().date()
        fecha_max = df["createdAt"].max().date()
        rango = st.date_input(
            "Período",
            value=(fecha_min, fecha_max),
            min_value=fecha_min,
            max_value=fecha_max,
        )

        # Agentes
        agentes_disponibles = sorted(df["agente_corto"].dropna().unique())
        agentes_sel = st.multiselect(
            "Agente(s)",
            options=agentes_disponibles,
            default=agentes_disponibles,
        )

        # Etapas del funnel
        etapas_disponibles = df["department"].value_counts().index.tolist()
        etapas_sel = st.multiselect(
            "Etapa del funnel",
            options=etapas_disponibles,
            default=etapas_disponibles,
        )

        st.markdown("---")
        st.caption(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if archivo is None:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                min-height:70vh;text-align:center;padding:40px;">
        <div style="font-size:56px;margin-bottom:20px;">💻</div>
        <h1 style="font-size:28px;font-weight:700;color:#0f172a;margin:0 0 8px;">
            Dashboard de Leads WhatsApp
        </h1>
        <p style="font-size:16px;color:#64748b;margin:0 0 32px;max-width:420px;">
            Sube el reporte de Whaticket para visualizar el análisis completo de leads.
        </p>
        <div style="background:#f8fafc;border:2px dashed #cbd5e1;border-radius:16px;
                    padding:32px 48px;max-width:420px;">
            <p style="font-size:14px;color:#475569;margin:0 0 8px;font-weight:600;">
                ← Abre el panel lateral izquierdo
            </p>
            <p style="font-size:13px;color:#94a3b8;margin:0;">
                y sube el archivo <strong>.xlsx</strong> exportado desde<br>
                Whaticket → Reportes → Conversaciones
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
# APLICAR FILTROS
# ─────────────────────────────────────────────

if len(rango) == 2:
    f_ini, f_fin = rango
else:
    f_ini = f_fin = rango[0]

mask = (
    (df["createdAt"].dt.date >= f_ini)
    & (df["createdAt"].dt.date <= f_fin)
    & (df["agente_corto"].isin(agentes_sel))
    & (df["department"].isin(etapas_sel))
)
dff = df[mask].copy()

if dff.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.markdown(
    f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:0 0 16px;border-bottom:1px solid #e2e8f0;margin-bottom:20px;">
        <div>
            <h1 style="font-size:22px;font-weight:700;color:#0f172a;margin:0;">
                Dashboard de Leads WhatsApp
            </h1>
            <p style="font-size:13px;color:#64748b;margin:4px 0 0;">
                Porlles · {f_ini.strftime('%d %b')} – {f_fin.strftime('%d %b %Y')} ·
                {len(dff):,} conversaciones filtradas
            </p>
        </div>
        <div style="text-align:right;">
            <span style="font-size:12px;color:#94a3b8;">Fuente: Whaticket</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# SECCIÓN 1: KPIs PRINCIPALES
# ─────────────────────────────────────────────

st.markdown('<div class="section-header">Resumen ejecutivo</div>', unsafe_allow_html=True)

total        = len(dff)
unicos       = dff["celular_norm"].nunique()
nuevos       = (dff["isNewContact"] == True).sum()
compraron    = (dff["department"] == "COMPRARON CON NOSOTROS 🏆").sum()
zona_hot     = (dff["department"] == "ZONA HOT 🔥").sum()
interesados  = (dff["department"] == "INTERESADO-SEGUIMIENTO ⏳ porlles").sum()
basura       = (dff["department"] == "BASURA").sum()
cotizando    = dff["es_cotizando"].sum()
sin_numero   = dff["contactNumber"].isna().sum()
conv_pct     = round(compraron / total * 100, 1) if total > 0 else 0
calif_pct    = round((interesados + zona_hot + compraron) / total * 100, 1) if total > 0 else 0
resp_prom    = dff["resp_h"].dropna().mean()

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.markdown(metric_card("Chats totales", f"{total:,}",
                            f"{unicos:,} únicos por número", "neutral"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("Nuevos contactos", f"{nuevos:,}",
                            f"{round(nuevos/total*100,1)}% del total", "neutral"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Interesados", f"{interesados:,}",
                            f"{calif_pct}% calificación", "neutral"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("Zona Hot", f"{zona_hot:,}",
                            "Listos para cerrar", "neutral"), unsafe_allow_html=True)
with c5:
    st.markdown(metric_card("Compraron", f"{compraron:,}",
                            f"{conv_pct}% conversión", "pos" if conv_pct > 1 else "neutral"), unsafe_allow_html=True)
with c6:
    resp_str = f"{round(resp_prom,1)}h promedio" if pd.notna(resp_prom) else "N/D"
    st.markdown(metric_card("T. respuesta", resp_str,
                            "Horas hábiles", "neutral"), unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECCIÓN 2: FUNNEL + LEADS POR DÍA
# ─────────────────────────────────────────────

st.markdown('<div class="section-header">Funnel de conversión</div>', unsafe_allow_html=True)

col_funnel, col_daily = st.columns([1, 1.6])

with col_funnel:
    dept_counts = dff["department"].value_counts().to_dict()

    labels_f, values_f, colors_f = [], [], []
    for dept in FUNNEL_ORDEN:
        if dept not in dept_counts:
            continue
        labels_f.append(FUNNEL_LABELS.get(dept, dept))
        values_f.append(dept_counts[dept])
        colors_f.append(FUNNEL_COLORES.get(dept, "#94a3b8"))

    pcts_f = [round(v / total * 100, 1) for v in values_f]

    fig_funnel = go.Figure(go.Bar(
        x=values_f,
        y=labels_f,
        orientation="h",
        marker_color=colors_f,
        text=[f"{v:,}  ({p}%)" for v, p in zip(values_f, pcts_f)],
        textposition="outside",
        textfont=dict(size=11, color="#334155"),
        hovertemplate="<b>%{y}</b><br>%{x:,} leads<extra></extra>",
        cliponaxis=False,
    ))
    fig_funnel.update_layout(
        height=300,
        margin=dict(l=0, r=90, t=10, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(
            showgrid=True, gridcolor="#f1f5f9",
            tickfont=dict(size=11, color="#64748b"),
            showticklabels=False,
        ),
        yaxis=dict(tickfont=dict(size=12, color="#334155"), autorange="reversed"),
        showlegend=False,
        bargap=0.3,
    )
    st.plotly_chart(fig_funnel, width='stretch')

with col_daily:
    leads_dia = dff.groupby("fecha").size().reset_index(name="leads")
    leads_dia["fecha"] = pd.to_datetime(leads_dia["fecha"])

    fig_daily = go.Figure()
    fig_daily.add_trace(go.Bar(
        x=leads_dia["fecha"],
        y=leads_dia["leads"],
        marker_color=[
            "#ef4444" if v >= leads_dia["leads"].quantile(0.85) else "#3b82f6"
            for v in leads_dia["leads"]
        ],
        hovertemplate="<b>%{x|%d %b}</b><br>Leads: %{y}<extra></extra>",
    ))
    fig_daily.update_layout(
        title=dict(text="Leads por día", font=dict(size=14, color="#0f172a"), x=0),
        height=280,
        margin=dict(l=0, r=0, t=36, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, tickformat="%d %b", tickfont=dict(size=11, color="#64748b")),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont=dict(size=11, color="#64748b")),
        bargap=0.25,
        showlegend=False,
    )
    st.plotly_chart(fig_daily, width='stretch')


# ─────────────────────────────────────────────
# SECCIÓN 3: RENDIMIENTO POR AGENTE
# ─────────────────────────────────────────────

st.markdown('<div class="section-header">Rendimiento por agente</div>', unsafe_allow_html=True)

col_tabla, col_pie = st.columns([1.6, 1])

with col_tabla:
    resumen_agente = dff.groupby("agente_corto").agg(
        Leads         = ("contactName", "count"),
        Nuevos        = ("isNewContact", lambda x: (x == True).sum()),
        Interesados   = ("department", lambda x: (x == "INTERESADO-SEGUIMIENTO ⏳ porlles").sum()),
        Zona_Hot      = ("department", lambda x: (x == "ZONA HOT 🔥").sum()),
        Compraron     = ("department", lambda x: (x == "COMPRARON CON NOSOTROS 🏆").sum()),
        Basura        = ("department", lambda x: (x == "BASURA").sum()),
        Resp_h        = ("resp_h", "mean"),
    ).reset_index()

    resumen_agente["Conv_%"]   = (resumen_agente["Compraron"] / resumen_agente["Leads"] * 100).round(1)
    resumen_agente["Calif_%"]  = ((resumen_agente["Interesados"] + resumen_agente["Zona_Hot"] + resumen_agente["Compraron"]) / resumen_agente["Leads"] * 100).round(1)
    resumen_agente["Basura_%"] = (resumen_agente["Basura"] / resumen_agente["Leads"] * 100).round(1)
    resumen_agente["Resp_h"]   = resumen_agente["Resp_h"].round(1).fillna(0)

    tbl = resumen_agente.sort_values("Leads", ascending=False)[
        ["agente_corto", "Leads", "Interesados", "Zona_Hot", "Compraron", "Conv_%", "Basura_%", "Resp_h"]
    ].copy()
    tbl.columns = ["Agente", "Leads", "Interesados", "Hot 🔥", "Cierres ✓", "Conv. %", "Basura %", "Resp. (h)"]

    max_conv   = max(float(tbl["Conv. %"].max()), 5.0)
    max_basura = max(float(tbl["Basura %"].max()), 10.0)

    st.dataframe(
        tbl,
        width='stretch',
        hide_index=True,
        column_config={
            "Conv. %": st.column_config.ProgressColumn(
                "Conv. %", help="% de leads que compraron",
                min_value=0, max_value=max_conv, format="%.1f%%",
            ),
            "Basura %": st.column_config.ProgressColumn(
                "Basura %", help="% de leads marcados como basura",
                min_value=0, max_value=max_basura, format="%.1f%%",
            ),
            "Resp. (h)": st.column_config.NumberColumn(
                "Resp. (h)", help="Tiempo de respuesta promedio (horas hábiles)", format="%.1f h",
            ),
        },
    )

with col_pie:
    # Donut de distribución por agente
    agente_dist = dff["agente_corto"].value_counts().reset_index()
    agente_dist.columns = ["Agente", "Leads"]
    colores_pie = [PALETA.get(a, "#94a3b8") for a in agente_dist["Agente"]]

    fig_pie = go.Figure(go.Pie(
        labels=agente_dist["Agente"],
        values=agente_dist["Leads"],
        hole=0.55,
        marker=dict(colors=colores_pie),
        textinfo="percent",
        textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>Leads: %{value}<br>%{percent}<extra></extra>",
    ))
    fig_pie.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:11px;'>leads</span>",
        x=0.5, y=0.5, font_size=18, showarrow=False
    )
    fig_pie.update_layout(
        title=dict(text="Distribución de leads", font=dict(size=14, color="#0f172a"), x=0),
        height=280,
        margin=dict(l=0, r=0, t=36, b=0),
        paper_bgcolor="white",
        legend=dict(font=dict(size=12), x=0.5, y=-0.1, xanchor="center", orientation="h"),
        showlegend=True,
    )
    st.plotly_chart(fig_pie, width='stretch')


# ─────────────────────────────────────────────
# SECCIÓN 4: COMPORTAMIENTO TEMPORAL
# ─────────────────────────────────────────────

st.markdown('<div class="section-header">Comportamiento temporal</div>', unsafe_allow_html=True)

col_hora, col_dow = st.columns(2)

with col_hora:
    hora_df = dff.groupby("hora").size().reset_index(name="leads")
    hora_df["color"] = hora_df["leads"].apply(
        lambda v: "#ef4444" if v >= hora_df["leads"].quantile(0.8) else "#0ea5e9"
    )

    fig_hora = go.Figure(go.Bar(
        x=hora_df["hora"],
        y=hora_df["leads"],
        marker_color=hora_df["color"],
        hovertemplate="<b>%{x}:00h</b><br>Leads: %{y}<extra></extra>",
    ))
    fig_hora.update_layout(
        title=dict(text="Leads por hora del día", font=dict(size=14, color="#0f172a"), x=0),
        height=240,
        margin=dict(l=0, r=0, t=36, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(
            tickvals=list(range(0, 24)),
            ticktext=[f"{h}h" for h in range(0, 24)],
            tickfont=dict(size=10, color="#64748b"),
            showgrid=False,
        ),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont=dict(size=11, color="#64748b")),
        bargap=0.15,
        showlegend=False,
        annotations=[dict(
            x=12.5, y=hora_df["leads"].max() * 1.05,
            text="Pico 10h–13h", showarrow=False,
            font=dict(size=11, color="#64748b"),
        )]
    )
    st.plotly_chart(fig_hora, width='stretch')

with col_dow:
    dow_df = dff.groupby("dow_es").size().reset_index(name="leads")
    dow_df["dow_es"] = pd.Categorical(dow_df["dow_es"], categories=DOW_ORDEN, ordered=True)
    dow_df = dow_df.sort_values("dow_es")
    dow_df["color"] = dow_df["leads"].apply(
        lambda v: "#7c3aed" if v >= dow_df["leads"].quantile(0.7) else "#94a3b8"
    )

    fig_dow = go.Figure(go.Bar(
        x=dow_df["dow_es"],
        y=dow_df["leads"],
        marker_color=dow_df["color"],
        hovertemplate="<b>%{x}</b><br>Leads: %{y}<extra></extra>",
    ))
    fig_dow.update_layout(
        title=dict(text="Leads por día de semana", font=dict(size=14, color="#0f172a"), x=0),
        height=240,
        margin=dict(l=0, r=0, t=36, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(tickfont=dict(size=11, color="#64748b"), showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont=dict(size=11, color="#64748b")),
        bargap=0.3,
        showlegend=False,
    )
    st.plotly_chart(fig_dow, width='stretch')


# ─────────────────────────────────────────────
# SECCIÓN 5: MAPA DE CALOR AGENTE × ETAPA
# ─────────────────────────────────────────────

st.markdown('<div class="section-header">Distribución detallada por agente y etapa</div>', unsafe_allow_html=True)

pivot = dff.groupby(["agente_corto", "department"]).size().unstack(fill_value=0)
pivot_norm = pivot.div(pivot.sum(axis=1), axis=0).round(3)

fig_heat = go.Figure(go.Heatmap(
    z=pivot_norm.values * 100,
    x=[FUNNEL_LABELS.get(c, c) for c in pivot_norm.columns],
    y=pivot_norm.index.tolist(),
    colorscale=[
        [0.0, "#f8fafc"], [0.3, "#bfdbfe"], [0.6, "#3b82f6"], [1.0, "#1e3a8a"]
    ],
    text=[[f"{v:.1f}%" for v in row] for row in pivot_norm.values * 100],
    texttemplate="%{text}",
    textfont=dict(size=12),
    hovertemplate="<b>%{y}</b> → %{x}<br>%{z:.1f}% de sus leads<extra></extra>",
    showscale=False,
))
fig_heat.update_layout(
    height=160 + len(pivot_norm) * 40,
    margin=dict(l=0, r=0, t=10, b=60),
    paper_bgcolor="white",
    plot_bgcolor="white",
    xaxis=dict(tickfont=dict(size=11, color="#475569"), side="bottom"),
    yaxis=dict(tickfont=dict(size=12, color="#0f172a")),
)
st.plotly_chart(fig_heat, width='stretch')


# ─────────────────────────────────────────────
# SECCIÓN 6: TAGS Y SEÑALES DE MERCADO
# ─────────────────────────────────────────────

st.markdown('<div class="section-header">Señales del mercado (etiquetas de chats)</div>', unsafe_allow_html=True)

col_tags, col_marcas, col_asesora = st.columns(3)

with col_tags:
    st.markdown("**Leads cotizando activamente**")
    n_cotizando = dff["es_cotizando"].sum()
    st.markdown(
        f'<p style="font-size:32px;font-weight:700;color:#3b82f6;margin:4px 0;">{n_cotizando}</p>'
        f'<p style="font-size:13px;color:#64748b;margin:0;">{round(n_cotizando/total*100,1)}% del total · en seguimiento activo</p>',
        unsafe_allow_html=True
    )
    st.markdown("<br>**NCA (No cierra ahora)**")
    n_nca = dff["es_nca"].sum()
    st.markdown(
        f'<p style="font-size:32px;font-weight:700;color:#f59e0b;margin:4px 0;">{n_nca}</p>'
        f'<p style="font-size:13px;color:#64748b;margin:0;">{round(n_nca/total*100,1)}% del total · calificados pero no listos</p>',
        unsafe_allow_html=True
    )

with col_marcas:
    st.markdown("**Marcas más solicitadas**")
    marcas_dict = {
        "ASUS": 7, "ACER / Predator": 6, "MSI": 3,
        "LENOVO / Legion": 2, "APPLE": 1, "ALIENWARE": 1
    }
    for marca, cnt in marcas_dict.items():
        ancho = round(cnt / 7 * 100)
        st.markdown(
            f"""
            <div style="margin:6px 0;">
                <div style="display:flex;justify-content:space-between;font-size:12px;
                            color:#475569;margin-bottom:3px;">
                    <span>{marca}</span><span style="font-weight:600;">{cnt}</span>
                </div>
                <div style="background:#f1f5f9;border-radius:3px;height:6px;">
                    <div style="background:#3b82f6;width:{ancho}%;height:6px;border-radius:3px;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

with col_asesora:
    st.markdown("**Asesora de destino (en tag)**")
    asesora_dist = dff["asesora_destino"].value_counts().head(6)
    for nombre, cnt in asesora_dist.items():
        if nombre == "Sin asignar":
            continue
        pct = round(cnt / dff["asesora_destino"].value_counts().sum() * 100, 1)
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:10px;margin:7px 0;font-size:13px;">
                <span style="color:#0f172a;font-weight:500;width:80px;">{nombre}</span>
                <div style="flex:1;background:#f1f5f9;border-radius:3px;height:8px;">
                    <div style="background:#7c3aed;width:{pct}%;height:8px;border-radius:3px;"></div>
                </div>
                <span style="color:#64748b;font-size:12px;width:50px;text-align:right;">{cnt} leads</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    n_redes = dff["es_redes"].sum()
    st.markdown(
        f"""<div style="margin-top:16px;padding:10px;background:#fef9c3;border-radius:8px;font-size:12px;color:#78350f;">
        <strong>Redes sociales detectadas:</strong> {n_redes} leads con tag "REDES SOCIALES".
        Atribución manual — el canal real no es capturado automáticamente.
        </div>""",
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────
# SECCIÓN 7: ALERTAS EJECUTIVAS
# ─────────────────────────────────────────────

st.markdown('<div class="section-header">Alertas y oportunidades</div>', unsafe_allow_html=True)

sin_resolucion = dff["resolvedAt"].isna().sum()
hot_sin_cierre = zona_hot - compraron
sin_num_count  = dff["contactNumber"].isna().sum()
pamela_basura  = dff[(dff["agente_corto"] == "KARINA") & (dff["department"] == "BASURA")].shape[0]
pamela_total   = dff[dff["agente_corto"] == "KARINA"].shape[0]
pamela_basura_pct = round(pamela_basura / pamela_total * 100, 1) if pamela_total else 0

col_a1, col_a2 = st.columns(2)

with col_a1:
    if sin_resolucion > total * 0.9:
        st.markdown(
            f'<div class="alert-danger"><strong>⚠ {sin_resolucion:,} chats sin resolución formal</strong> — '
            f'Nadie presionó "Resolver" en Whaticket. La tasa de cierre real no puede medirse automáticamente.</div>',
            unsafe_allow_html=True
        )
    if hot_sin_cierre > 0:
        st.markdown(
            f'<div class="alert-warning"><strong>🔥 {hot_sin_cierre} leads Hot sin cierre registrado</strong> — '
            f'Entraron a Zona Hot pero no tienen etapa de compra. Revisar seguimiento.</div>',
            unsafe_allow_html=True
        )
    if pamela_basura_pct > 10:
        st.markdown(
            f'<div class="alert-warning"><strong>🗑 Karina: {pamela_basura_pct}% de leads a Basura</strong> — '
            f'Criterios de calificación posiblemente no estandarizados entre agentes.</div>',
            unsafe_allow_html=True
        )

with col_a2:
    chelsea_compraron = dff[(dff["agente_corto"] == "CHELSEA") & (dff["department"] == "COMPRARON CON NOSOTROS 🏆")].shape[0]
    chelsea_total = dff[dff["agente_corto"] == "CHELSEA"].shape[0]
    chelsea_resp  = dff[dff["agente_corto"] == "CHELSEA"]["resp_h"].mean()
    chelsea_resp_str = f"{round(chelsea_resp, 1)}h" if pd.notna(chelsea_resp) else "N/D"
    if chelsea_compraron == 0 and chelsea_total > 0:
        st.markdown(
            f'<div class="alert-info"><strong>💡 Chelsea: {chelsea_total} leads, 0 cierres</strong> — '
            f'Tiempo de respuesta promedio: {chelsea_resp_str}. Verificar si su rol es cierre o solo primer filtro.</div>',
            unsafe_allow_html=True
        )
    if sin_num_count > 0:
        st.markdown(
            f'<div class="alert-info"><strong>📵 {sin_num_count} leads sin número de teléfono</strong> — '
            f'No se pueden cruzar con el Excel de ventas. Completar datos en Whaticket.</div>',
            unsafe_allow_html=True
        )
    if dff[dff["dow_es"].isin(["Lunes", "Martes"])].shape[0] > total * 0.4:
        st.markdown(
            f'<div class="alert-success"><strong>📅 Lunes y martes concentran el mayor volumen</strong> — '
            f'Considerar refuerzo de cobertura esos días y usar Mié–Jue para seguimiento de calientes.</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────
# SECCIÓN 8: TABLA DE DETALLE (EXPANDIBLE)
# ─────────────────────────────────────────────

with st.expander("Ver detalle de conversaciones", expanded=False):
    cols_show = [
        "createdAt", "contactName", "celular_norm", "agente_corto",
        "department", "resp_h", "es_cotizando", "es_nca", "tags"
    ]
    cols_rename = {
        "createdAt":    "Fecha",
        "contactName":  "Contacto",
        "celular_norm": "Número",
        "agente_corto": "Agente",
        "department":   "Etapa",
        "resp_h":       "Resp. (h)",
        "es_cotizando": "Cotizando",
        "es_nca":       "NCA",
        "tags":         "Tags",
    }
    df_tabla = dff[cols_show].rename(columns=cols_rename).copy()
    df_tabla["Fecha"] = df_tabla["Fecha"].dt.strftime("%d/%m %H:%M")
    df_tabla["Resp. (h)"] = df_tabla["Resp. (h)"].round(1)
    df_tabla["Cotizando"] = df_tabla["Cotizando"].map({True: "✓", False: ""})
    df_tabla["NCA"] = df_tabla["NCA"].map({True: "✓", False: ""})

    st.dataframe(
        df_tabla,
        width='stretch',
        height=400,
        hide_index=True,
    )

    csv = df_tabla.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Descargar CSV filtrado",
        data=csv,
        file_name=f"porlles_leads_{f_ini}_{f_fin}.csv",
        mime="text/csv",
    )


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown(
    """
    <div style="margin-top:40px;padding-top:16px;border-top:1px solid #e2e8f0;
                font-size:11px;color:#94a3b8;text-align:center;">
        Porlles · Dashboard de Leads WhatsApp · Datos: Whaticket Conversations Report
    </div>
    """,
    unsafe_allow_html=True,
)
