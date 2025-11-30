import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import os

# ---------------------------
# Configuración de la página
# ---------------------------
st.set_page_config(
    page_title="Sistema de Gestión Ambiental - Intercambiadores de Calor",
    page_icon="♻️",
    layout="wide"
)

# ---------------------------
# Estilo CSS personalizado
# ---------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .alert-critical {
        background-color: #ff4444;
        padding: 10px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
    .alert-warning {
        background-color: #ffbb33;
        padding: 10px;
        border-radius: 5px;
        color: #333;
        font-weight: bold;
    }
    .small-note {
        font-size: 0.85rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Datos de ejemplo
# ---------------------------
@st.cache_data
def generar_datos_ejemplo():
    fechas = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    datos = {
        'fecha': fechas,
        'consumo_energia_kwh': [random.randint(8000, 12000) for _ in range(len(fechas))],
        'consumo_agua_m3': [random.randint(50, 150) for _ in range(len(fechas))],
        'residuos_peligrosos_kg': [random.randint(20, 80) for _ in range(len(fechas))],
        'emisiones_co2_ton': [random.uniform(2.5, 5.5) for _ in range(len(fechas))],
        'cobre_reciclado_porcentaje': [random.randint(25, 45) for _ in range(len(fechas))],
        'eficiencia_termica': [random.uniform(85, 95) for _ in range(len(fechas))],
    }
    return pd.DataFrame(datos)

df_produccion = generar_datos_ejemplo()

# ---------------------------
# Variables críticas por etapa del proceso
# (Se mantienen los datos iniciales)
# ---------------------------
variables_criticas = {
    'Selección y Preparación': {
        'Consumo energético (molienda)': {'actual': 8500, 'objetivo': 7500, 'unidad': 'kWh'},
        'Pureza del cobre': {'actual': 99.95, 'objetivo': 99.90, 'unidad': '%'},
        'Material reciclado': {'actual': 35, 'objetivo': 50, 'unidad': '%'}
    },
    'Fabricación de Tubos': {
        'Consumo agua proceso': {'actual': 120, 'objetivo': 100, 'unidad': 'm³'},
        'Residuos metálicos': {'actual': 45, 'objetivo': 30, 'unidad': 'kg'},
        'Eficiencia extrusión': {'actual': 88, 'objetivo': 92, 'unidad': '%'}
    },
    'Limpieza Química': {
        'Ácidos agotados': {'actual': 65, 'objetivo': 40, 'unidad': 'L'},
        'Metales pesados en efluente': {'actual': 15, 'objetivo': 10, 'unidad': 'mg/L'},
        'Reutilización de solventes': {'actual': 40, 'objetivo': 70, 'unidad': '%'}
    },
    'Mecanizado': {
        'Fluidos de corte usados': {'actual': 80, 'objetivo': 50, 'unidad': 'L'},
        'Virutas recuperadas': {'actual': 75, 'objetivo': 90, 'unidad': '%'},
        'Emisiones VOC': {'actual': 12, 'objetivo': 8, 'unidad': 'mg/m³'}
    },
    'Soldadura/Brazing': {
        'Consumo gas inerte': {'actual': 50, 'objetivo': 40, 'unidad': 'm³'},
        'Tasa de rechazo': {'actual': 3.5, 'objetivo': 2.0, 'unidad': '%'},
        'Energía horno': {'actual': 1200, 'objetivo': 1000, 'unidad': 'kWh'}
    }
}

# ---------------------------
# ODS relacionados y mapeo automático
# ---------------------------
ods_relacionados = {
    'ODS 6': {'nombre': 'Agua Limpia y Saneamiento', 'cumplimiento': 72},
    'ODS 7': {'nombre': 'Energía Asequible y No Contaminante', 'cumplimiento': 68},
    'ODS 9': {'nombre': 'Industria, Innovación e Infraestructura', 'cumplimiento': 85},
    'ODS 12': {'nombre': 'Producción y Consumo Responsables', 'cumplimiento': 75},
    'ODS 13': {'nombre': 'Acción por el Clima', 'cumplimiento': 70}
}

ods_auto_relacion = {
    "agua": "ODS 6 - Agua Limpia y Saneamiento",
    "energia": "ODS 7 - Energía Asequible y No Contaminante",
    "residuos": "ODS 12 - Producción y Consumo Responsables",
    "emisiones": "ODS 13 - Acción por el Clima",
    "innovacion": "ODS 9 - Industria, Innovación e Infraestructura"
}

def identificar_ods(variable):
    """Identifica automáticamente un ODS probable a partir del nombre de la variable."""
    v = variable.lower()
    if "agua" in v or "efluente" in v:
        return ods_auto_relacion["agua"]
    if "energ" in v or "energia" in v or "kwh" in v:
        return ods_auto_relacion["energia"]
    if "residuo" in v or "residuos" in v or "lodos" in v:
        return ods_auto_relacion["residuos"]
    if "co2" in v or "emision" in v or "voc" in v:
        return ods_auto_relacion["emisiones"]
    return ods_auto_relacion["innovacion"]

# ---------------------------
# Inicializar almacenamiento de datos ingresados y alertas
# ---------------------------
if 'datos_ingresados' not in st.session_state:
    st.session_state.datos_ingresados = {}
if 'evaluar' not in st.session_state:
    st.session_state.evaluar = False
if 'simular' not in st.session_state:
    st.session_state.simular = False
if 'lotes_registrados' not in st.session_state:
    st.session_state.lotes_registrados = {}
    # Ejemplos
    st.session_state.lotes_registrados['LOTE-2024-1205'] = {
        'Origen': 'Mina Los Pelambres, Chile',
        'Tipo': 'Cobre electrolítico C12200',
        'Contenido reciclado': '42%',
        'Pureza': '99.95%',
        'Fecha ingreso': '2024-11-15',
        'Masa total': '1,250 kg',
        'Estado': 'En proceso - Fabricación de tubos',
        'Certificación': 'ASTM B75 ✓'
    }
    st.session_state.lotes_registrados['LOTE-2024-1201'] = {
        'Origen': 'Reciclaje interno',
        'Tipo': 'Cobre reciclado C12200',
        'Contenido reciclado': '100%',
        'Pureza': '99.90%',
        'Fecha ingreso': '2024-11-10',
        'Masa total': '850 kg',
        'Estado': 'En proceso - Selección y Preparación',
        'Certificación': 'ASTM B75 ✓'
    }

if 'alert_counts' not in st.session_state:
    # Estructura: {'Etapa': {'variable': {'count': int, 'last_ts': iso}}}
    st.session_state.alert_counts = {}

if 'last_eval_ts' not in st.session_state:
    st.session_state.last_eval_ts = None

# Metodología por defecto (pasos)
if 'metodologia_steps' not in st.session_state:
    st.session_state.metodologia_steps = [
        {'paso': 'Identificar necesidad y objetivo', 'completado': False},
        {'paso': 'Seleccionar recursos y materias primas', 'completado': False},
        {'paso': 'Diseño del proceso y fases', 'completado': False},
        {'paso': 'Prueba de prototipo y control de calidad', 'completado': False},
        {'paso': 'Implementación y trazabilidad', 'completado': False},
        {'paso': 'Optimización y reducción de impactos', 'completado': False},
    ]

# ---------------------------
# Utilidades: generación de lote
# ---------------------------
def generar_codigo_lote():
    """Genera un código de lote automático"""
    fecha_actual = datetime.now()
    codigo = f"LOTE-{fecha_actual.strftime('%Y-%m%d-%H%M%S')}"
    return codigo

# ---------------------------
# Funciones de evaluación y recomendaciones
# ---------------------------
def evaluar_variable(valor_actual, valor_objetivo, tipo='menor_mejor'):
    """
    Evalúa una variable comparándola con su objetivo
    tipo: 'menor_mejor' (consumo, residuos) o 'mayor_mejor' (eficiencia, porcentajes positivos)
    Devuelve: dict con cumplimiento, estado, color, diferencia, diferencia_porcentual
    """
    # Manejo de cero en objetivo para evitar división por cero
    try:
        if tipo == 'menor_mejor':
            if valor_actual <= valor_objetivo:
                cumplimiento = 100.0
                estado = "✅ Cumple"
                color = "green"
            else:
                cumplimiento = (valor_objetivo / valor_actual) * 100 if valor_actual != 0 else 0
                if cumplimiento >= 80:
                    estado = "⚠️ Advertencia"
                    color = "orange"
                else:
                    estado = "🔴 No Cumple"
                    color = "red"
        else:
            if valor_actual >= valor_objetivo:
                cumplimiento = 100.0
                estado = "✅ Cumple"
                color = "green"
            else:
                cumplimiento = (valor_actual / valor_objetivo) * 100 if valor_objetivo != 0 else 0
                if cumplimiento >= 80:
                    estado = "⚠️ Advertencia"
                    color = "orange"
                else:
                    estado = "🔴 No Cumple"
                    color = "red"
    except Exception:
        cumplimiento = 0.0
        estado = "🔴 Error"
        color = "red"

    diferencia = valor_actual - valor_objetivo
    diferencia_porcentual = ((valor_actual - valor_objetivo) / valor_objetivo) * 100 if valor_objetivo != 0 else 0

    return {
        'cumplimiento': float(cumplimiento),
        'estado': estado,
        'color': color,
        'diferencia': diferencia,
        'diferencia_porcentual': diferencia_porcentual
    }

def determinar_tipo_variable(nombre_variable):
    """Determina si una variable es 'menor_mejor' o 'mayor_mejor'"""
    mayor_mejor_keywords = ['pureza', 'material reciclado', 'eficiencia', 'reutilización', 'virutas recuperadas', 'reciclado']
    nombre_lower = nombre_variable.lower()
    if any(k in nombre_lower for k in mayor_mejor_keywords):
        return 'mayor_mejor'
    return 'menor_mejor'

def recomendar_acciones(var_nombre, evaluacion):
    """
    Genera recomendaciones concretas según la variable y su evaluación.
    Retorna una lista de strings con acciones sugeridas.
    """
    recomendaciones = []
    diff_pct = evaluacion['diferencia_porcentual']
    estado = evaluacion['estado']
    v = var_nombre.lower()

    # Recomendaciones genéricas por tipo
    if 'agua' in v or 'efluente' in v:
        recomendaciones.append("Revisar pérdidas y fugas en circuito de agua.")
        recomendaciones.append("Evaluar sistemas de recirculación y recuperación de aguas de proceso.")
        if estado.startswith("🔴"):
            recomendaciones.append("Implementar tratamiento en línea y monitoreo de metales pesados.")
    if 'energ' in v or 'kwh' in v or 'molienda' in v:
        recomendaciones.append("Revisar eficiencia del molino y programación de mantenimiento preventivo.")
        recomendaciones.append("Analizar posibilidad de recuperación de calor o uso de motores de mayor eficiencia.")
        if diff_pct > 20:
            recomendaciones.append("Evaluar rediseño de parámetros de molienda para disminuir consumo.")
    if 'residuo' in v or 'lodos' in v or 'ácidos' in v or 'ácido' in v:
        recomendaciones.append("Segregar residuos en origen y establecer rutas de valorización.")
        recomendaciones.append("Implementar neutralización y tratamiento de ácidos antes del efluente.")
        if estado.startswith("🔴"):
            recomendaciones.append("Priorizar reducción en la fuente y buscar proveedores de reciclaje de subproductos.")
    if 'pureza' in v or 'virutas' in v:
        recomendaciones.append("Reforzar controles de calidad y procesos de purificación.")
        if estado.startswith("🔴"):
            recomendaciones.append("Ajustar parámetros de proceso y revisar materia prima.")
    if 'emision' in v or 'co2' in v or 'voc' in v:
        recomendaciones.append("Monitoreo continuo de emisiones y mejoras en captación.")
        recomendaciones.append("Optimizar hornos y procesos térmicos para reducir emisiones.")

    # Recomendaciones por magnitud del incumplimiento
    if estado.startswith("🔴"):
        recomendaciones.append("Plan de acción inmediato: asignar responsable y fecha límite para corrección.")
    elif estado.startswith("⚠️"):
        recomendaciones.append("Monitorear semanalmente y aplicar medidas de mejora en 30 días.")

    # Eliminar duplicados
    recomendaciones = list(dict.fromkeys(recomendaciones))
    return recomendaciones

# ---------------------------
# Simulación básica de escenario (mantener)
# ---------------------------
def simular_escenario(datos_base, cambios):
    datos_simulados = datos_base.copy()
    for etapa, variables in cambios.items():
        if etapa not in datos_simulados:
            datos_simulados[etapa] = {}
        datos_simulados[etapa].update(variables)
    return datos_simulados

# ---------------------------
# Sidebar - Navegación (agregada la página de Metodología y Desarrollo)
# ---------------------------
try:
    # Si no hay internet o la imagen remota falla, muestro texto
    st.sidebar.image("logo_utem.jpg", use_container_width=True)
except Exception:
    st.sidebar.markdown("### 🏛️ UTEM")

st.sidebar.title("📊 Navegación")
pagina = st.sidebar.selectbox(
    "Seleccione módulo:",
    ["Dashboard Principal", "Metodología y Desarrollo", "Ingreso y Evaluación", "Variables Críticas",
     "Simulación de Escenarios", "Economía Circular", "ODS y Cumplimiento", "Gestión de Residuos", "Reportes"]
)

# ---------------------------
# PÁGINA 1: DASHBOARD PRINCIPAL
# ---------------------------
if pagina == "Dashboard Principal":
    st.markdown('<p class="main-header">♻️ Sistema de Gestión Ambiental - Intercambiadores de Calor de Cobre</p>', unsafe_allow_html=True)

    # Mostrar la imagen cargada (tabla/instrucciones) si existe
    img_path = "/mnt/data/36518cf6-0c2f-4ac0-92ce-0c3731fa2f56.png"
    if os.path.exists(img_path):
        st.image(img_path, caption="Condiciones para la creación del sistema informático (referencia)", use_container_width=True)
    else:
        st.info("📎 Imagen de referencia no encontrada en /mnt/data - se utilizará el placeholder visual en el sistema.")

    st.markdown("### 📈 KPIs Principales del Mes")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="⚡ Consumo Energético",
            value="9,850 kWh",
            delta="-12% vs mes anterior",
            delta_color="inverse"
        )

    with col2:
        st.metric(
            label="💧 Consumo de Agua",
            value="98 m³",
            delta="-8% vs mes anterior",
            delta_color="inverse"
        )

    with col3:
        st.metric(
            label="♻️ Cobre Reciclado",
            value="38%",
            delta="+5% vs mes anterior"
        )

    with col4:
        st.metric(
            label="☁️ Emisiones CO₂",
            value="3.8 ton",
            delta="-15% vs mes anterior",
            delta_color="inverse"
        )

    st.markdown("---")

    # Gráficos principales
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Tendencia de Consumo Energético")
        fig_energia = px.line(
            df_produccion.tail(90),
            x='fecha',
            y='consumo_energia_kwh',
            title='Últimos 90 días'
        )
        fig_energia.add_hline(y=10000, line_dash="dash", line_color="red",
                              annotation_text="Límite objetivo")
        st.plotly_chart(fig_energia, use_container_width=True)

    with col2:
        st.markdown("#### 💧 Gestión de Recursos Hídricos")
        fig_agua = px.area(
            df_produccion.tail(90),
            x='fecha',
            y='consumo_agua_m3',
            title='Consumo de agua (m³)'
        )
        st.plotly_chart(fig_agua, use_container_width=True)

    # Alertas ambientales (calculo simple de condiciones actuales)
    st.markdown("### 🚨 Alertas Ambientales Activas")

    col1, col2 = st.columns(2)

    with col1:
        if variables_criticas['Limpieza Química']['Metales pesados en efluente']['actual'] > variables_criticas['Limpieza Química']['Metales pesados en efluente']['objetivo']:
            st.markdown('<div class="alert-critical">⚠️ CRÍTICO: Metales pesados en efluente superan límite</div>', unsafe_allow_html=True)
        else:
            st.success("✔ Efluentes dentro de los límites")

        # Alerta persistente basada en conteo
        # Si algún conteo supera 2, se muestra alerta para cambio de proceso
        persistent_alarms = []
        for etapa, vars_counts in st.session_state.alert_counts.items():
            for vname, cntinfo in vars_counts.items():
                if cntinfo['count'] >= 3:
                    persistent_alarms.append(f"{vname} en {etapa} (fuera de norma {cntinfo['count']} veces)")

        if persistent_alarms:
            st.markdown('<div class="alert-critical">🔴 Alerta: Variables con repetidos incumplimientos detectadas. Revisar procesos y considerar cambio.</div>', unsafe_allow_html=True)
            for a in persistent_alarms:
                st.write(f"- {a}")

    with col2:
        st.markdown('<div class="alert-warning">⚡ ADVERTENCIA: Consumo energético cerca del límite mensual</div>', unsafe_allow_html=True)
        st.markdown('<div class="alert-warning">♻️ ADVERTENCIA: Porcentaje de cobre reciclado bajo objetivo (38% < 50%)</div>', unsafe_allow_html=True)

# ---------------------------
# PÁGINA 2: METODOLOGÍA Y DESARROLLO
# ---------------------------
elif pagina == "Metodología y Desarrollo":
    st.markdown('<p class="main-header">🛠️ Metodología y Desarrollo del Prototipo</p>', unsafe_allow_html=True)

    # Mostrar la imagen que explica condiciones y la tabla si existe
    img_path = "/mnt/data/36518cf6-0c2f-4ac0-92ce-0c3731fa2f56.png"
    if os.path.exists(img_path):
        st.image(img_path, caption="Condiciones para la creación del sistema informático (tabla referencial)", use_container_width=True)

    st.markdown("### 📋 Pasos de la Metodología")
    # Mostrar checklist interactivo
    for i, paso in enumerate(st.session_state.metodologia_steps):
        cols = st.columns([0.1, 8, 1])
        with cols[0]:
            checked = st.checkbox("", value=paso['completado'], key=f"met_step_{i}")
        with cols[1]:
            st.write(f"**Paso {i+1}:** {paso['paso']}")
        with cols[2]:
            if checked != paso['completado']:
                # Actualizar estado
                st.session_state.metodologia_steps[i]['completado'] = checked

    st.markdown("---")
    # Mostrar progreso general
    total = len(st.session_state.metodologia_steps)
    completados = sum(1 for s in st.session_state.metodologia_steps if s['completado'])
    progreso = int((completados / total) * 100)
    st.progress(progreso / 100)
    st.markdown(f"**Progreso de metodología:** {completados}/{total} pasos completados ({progreso}%)")

    # Área para notas y plan de desarrollo
    st.markdown("### 📝 Notas y Plan de Desarrollo")
    plan_text = st.text_area("Describa el plan de desarrollo o resultados de la fase actual:", value="", height=150, key="plan_de_desarrollo")
    if st.button("💾 Guardar Plan de Desarrollo"):
        st.success("✅ Plan guardado en la sesión (temporal).")

    # Vinculación entre metodología y evaluación de variables (sugerencia)
    st.markdown("### 🔗 Recomendación automática según estado de etapas")
    recomendaciones_generales = []
    # Si las etapas de optimización no están completas, sugiero acciones
    if not st.session_state.metodologia_steps[-1]['completado']:
        recomendaciones_generales.append("Completar fase de 'Optimización y reducción de impactos' antes de la implementación final.")
    if not st.session_state.metodologia_steps[2]['completado']:
        recomendaciones_generales.append("Revisar el 'Diseño del proceso y fases' para identificar puntos de control críticos.")
    if recomendaciones_generales:
        for rec in recomendaciones_generales:
            st.markdown(f"- {rec}")
    else:
        st.success("La metodología está completada o avanzada. Puede proceder a implementación.")

# ---------------------------
# PÁGINA 3: INGRESO Y EVALUACIÓN DE DATOS
# ---------------------------
elif pagina == "Ingreso y Evaluación":
    st.markdown('<p class="main-header">📝 Ingreso y Evaluación de Datos</p>', unsafe_allow_html=True)

    st.markdown("### 🎯 Ingrese los datos de medición para evaluar el cumplimiento de variables críticas")

    # Seleccionar etapa
    etapa_seleccionada = st.selectbox(
        "Seleccione la etapa del proceso:",
        list(variables_criticas.keys()),
        key="etapa_evaluacion"
    )

    st.markdown(f"### 📌 Etapa: {etapa_seleccionada}")
    st.markdown("---")

    # Formulario para ingresar datos
    variables_etapa = variables_criticas[etapa_seleccionada]
    datos_formulario = {}

    st.markdown("#### 📊 Ingrese los valores medidos:")

    col1, col2 = st.columns(2)

    with col1:
        for i, (var_nombre, var_data) in enumerate(variables_etapa.items()):
            if i % 2 == 0:
                valor_guardado = st.session_state.datos_ingresados.get(etapa_seleccionada, {}).get(var_nombre, var_data['actual'])
                valor = st.number_input(
                    f"{var_nombre} ({var_data['unidad']})",
                    min_value=0.0,
                    value=float(valor_guardado),
                    step=0.1,
                    key=f"input_{etapa_seleccionada}_{var_nombre}",
                    help=f"Objetivo: {var_data['objetivo']} {var_data['unidad']}"
                )
                datos_formulario[var_nombre] = valor

    with col2:
        for i, (var_nombre, var_data) in enumerate(variables_etapa.items()):
            if i % 2 == 1:
                valor_guardado = st.session_state.datos_ingresados.get(etapa_seleccionada, {}).get(var_nombre, var_data['actual'])
                valor = st.number_input(
                    f"{var_nombre} ({var_data['unidad']})",
                    min_value=0.0,
                    value=float(valor_guardado),
                    step=0.1,
                    key=f"input_{etapa_seleccionada}_{var_nombre}_2",
                    help=f"Objetivo: {var_data['objetivo']} {var_data['unidad']}"
                )
                datos_formulario[var_nombre] = valor

    # Si hay número impar de variables, agregar la última
    if len(variables_etapa) % 2 == 1:
        var_nombre = list(variables_etapa.keys())[-1]
        var_data = variables_etapa[var_nombre]
        if var_nombre not in datos_formulario:
            valor_guardado = st.session_state.datos_ingresados.get(etapa_seleccionada, {}).get(var_nombre, var_data['actual'])
            valor = st.number_input(
                f"{var_nombre} ({var_data['unidad']})",
                min_value=0.0,
                value=float(valor_guardado),
                step=0.1,
                key=f"input_{etapa_seleccionada}_{var_nombre}_final",
                help=f"Objetivo: {var_data['objetivo']} {var_data['unidad']}"
            )
            datos_formulario[var_nombre] = valor

    # Botones de acción
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Guardar Datos", type="primary", use_container_width=True):
            if etapa_seleccionada not in st.session_state.datos_ingresados:
                st.session_state.datos_ingresados[etapa_seleccionada] = {}
            st.session_state.datos_ingresados[etapa_seleccionada].update(datos_formulario)
            # Resetear contador de alertas para esas variables (opcional)
            if etapa_seleccionada in st.session_state.alert_counts:
                # no borramos el historial, solo dejamos registro; si desea resetear: descomentar
                pass
            st.success(f"✅ Datos de {etapa_seleccionada} guardados correctamente")
            st.rerun()

    with col2:
        if st.button("📊 Evaluar Datos", use_container_width=True):
            # Dejar marca temporal para evitar incrementar múltiples veces por rerun automático
            st.session_state.last_eval_ts = datetime.now().isoformat()
            st.session_state.evaluar = True

    with col3:
        if st.button("🔄 Limpiar Datos", use_container_width=True):
            if etapa_seleccionada in st.session_state.datos_ingresados:
                del st.session_state.datos_ingresados[etapa_seleccionada]
            st.success("✅ Datos limpiados")
            st.rerun()

    st.markdown("---")

    # Mostrar evaluación si se solicitó
    if st.session_state.get('evaluar', False) or datos_formulario:
        st.markdown("### 📈 Resultados de la Evaluación")

        evaluaciones = []
        cumplimientos = []

        for var_nombre, var_data in variables_etapa.items():
            valor_actual = datos_formulario.get(var_nombre, var_data['actual'])
            valor_objetivo = var_data['objetivo']
            tipo = determinar_tipo_variable(var_nombre)
            evaluacion = evaluar_variable(valor_actual, valor_objetivo, tipo)
            evaluaciones.append({
                'variable': var_nombre,
                'actual': valor_actual,
                'objetivo': valor_objetivo,
                'unidad': var_data['unidad'],
                'evaluacion': evaluacion
            })
            cumplimientos.append(evaluacion['cumplimiento'])

            # Actualizar contadores de alerta si es una evaluación disparada por botón Evaluar
            # Prevenir incrementos múltiples: solo incrementar si last_eval_ts nuevo
            ts = st.session_state.last_eval_ts
            if ts:
                etapa_counts = st.session_state.alert_counts.get(etapa_seleccionada, {})
                var_info = etapa_counts.get(var_nombre, {'count': 0, 'last_ts': None})
                if var_info.get('last_ts') != ts:
                    if evaluacion['estado'].startswith("🔴"):
                        var_info['count'] = var_info.get('count', 0) + 1
                    var_info['last_ts'] = ts
                    etapa_counts[var_nombre] = var_info
                    st.session_state.alert_counts[etapa_seleccionada] = etapa_counts

        # Mostrar resultados en columnas y recomendaciones/ODS
        for eval_data in evaluaciones:
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

            with col1:
                st.markdown(f"**{eval_data['variable']}**")
                # ODS detectado
                ods_detectado = identificar_ods(eval_data['variable'])
                st.markdown(f"🌍 **ODS relacionado:** `{ods_detectado}`")
            with col2:
                st.metric("Medido", f"{eval_data['actual']:.2f} {eval_data['unidad']}")
            with col3:
                st.metric("Objetivo", f"{eval_data['objetivo']:.2f} {eval_data['unidad']}")
            with col4:
                st.markdown(f"<span style='color: {eval_data['evaluacion']['color']}; font-weight: bold;'>{eval_data['evaluacion']['estado']}</span>",
                           unsafe_allow_html=True)
            with col5:
                st.metric("Cumplimiento", f"{eval_data['evaluacion']['cumplimiento']:.1f}%")

            # Barra de progreso con color aproximado
            progreso_bar = max(0.0, min(eval_data['evaluacion']['cumplimiento'] / 100.0, 1.0))
            st.progress(progreso_bar)

            # Recomendaciones automáticas
            recomendaciones = recomendar_acciones(eval_data['variable'], eval_data['evaluacion'])
            if recomendaciones:
                st.markdown("**Recomendaciones:**")
                for r in recomendaciones:
                    st.markdown(f"- {r}")

            # Mostrar conteo de alertas históricas para la variable
            cnt = st.session_state.alert_counts.get(etapa_seleccionada, {}).get(eval_data['variable'], {}).get('count', 0)
            if cnt > 0:
                if cnt >= 3:
                    st.markdown(f"<span style='color: red; font-weight:bold;'>🔴 Historial: {cnt} incumplimientos (recomendado: revisar cambio de proceso)</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color: orange;'>⚠ Historial: {cnt} incumplimientos</span>", unsafe_allow_html=True)

            st.markdown("---")

        # Resumen de cumplimiento de la etapa
        cumplimiento_promedio = sum(cumplimientos) / len(cumplimientos) if cumplimientos else 0

        st.markdown("### 📊 Resumen de Cumplimiento de la Etapa")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Cumplimiento Promedio", f"{cumplimiento_promedio:.1f}%")

        with col2:
            if cumplimiento_promedio >= 100:
                estado_general = "✅ Excelente"
                color_general = "green"
            elif cumplimiento_promedio >= 80:
                estado_general = "⚠️ Aceptable"
                color_general = "orange"
            else:
                estado_general = "🔴 Requiere Atención"
                color_general = "red"
            st.markdown(f"<span style='color: {color_general}; font-size: 1.5rem; font-weight: bold;'>{estado_general}</span>",
                       unsafe_allow_html=True)

        with col3:
            variables_cumplen = sum(1 for e in evaluaciones if e['evaluacion']['cumplimiento'] >= 100)
            st.metric("Variables que Cumplen", f"{variables_cumplen}/{len(evaluaciones)}")

        # Gráfico de cumplimiento
        df_eval = pd.DataFrame([
            {
                'Variable': e['variable'],
                'Cumplimiento (%)': e['evaluacion']['cumplimiento'],
                'Estado': e['evaluacion']['estado']
            }
            for e in evaluaciones
        ])

        fig_eval = px.bar(
            df_eval,
            x='Variable',
            y='Cumplimiento (%)',
            color='Cumplimiento (%)',
            color_continuous_scale=['red', 'yellow', 'green'],
            title='Cumplimiento por Variable',
            text='Cumplimiento (%)'
        )
        fig_eval.add_hline(y=100, line_dash="dash", line_color="blue",
                          annotation_text="Objetivo 100%")
        fig_eval.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_eval.update_layout(height=400)
        st.plotly_chart(fig_eval, use_container_width=True)

        # Reiniciar flag evaluar
        st.session_state.evaluar = False

# ---------------------------
# PÁGINA 4: VARIABLES CRÍTICAS
# ---------------------------
elif pagina == "Variables Críticas":
    st.markdown('<p class="main-header">🎯 Monitoreo de Variables Críticas por Etapa</p>', unsafe_allow_html=True)

    etapa_seleccionada = st.selectbox(
        "Seleccione etapa del proceso:",
        list(variables_criticas.keys())
    )

    st.markdown(f"### 📌 Etapa: {etapa_seleccionada}")

    variables = variables_criticas[etapa_seleccionada]

    for var_nombre, var_data in variables.items():
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"**{var_nombre}**")
            progreso = (var_data['actual'] / var_data['objetivo']) * 100 if var_data['objetivo'] != 0 else 0
            color = "green" if progreso <= 100 else "red" if progreso > 120 else "orange"
            st.progress(min(progreso / 100, 1.0))

        with col2:
            st.metric("Actual", f"{var_data['actual']} {var_data['unidad']}")

        with col3:
            st.metric("Objetivo", f"{var_data['objetivo']} {var_data['unidad']}")

        # Identificar ODS y mostrar
        ods_detect = identificar_ods(var_nombre)
        st.markdown(f"🌍 **ODS:** {ods_detect}")

        st.markdown("---")

    # Gráfico de cumplimiento por etapa
    st.markdown("### 📊 Cumplimiento de Objetivos por Etapa")

    cumplimiento_data = []
    for etapa, variables in variables_criticas.items():
        cumplimiento_total = 0
        for var_data in variables.values():
            if var_data['actual'] <= var_data['objetivo']:
                cumplimiento_total += 100
            else:
                cumplimiento_total += (var_data['objetivo'] / var_data['actual']) * 100 if var_data['actual'] != 0 else 0
        cumplimiento_promedio = cumplimiento_total / len(variables)
        cumplimiento_data.append({'Etapa': etapa, 'Cumplimiento': cumplimiento_promedio})

    df_cumplimiento = pd.DataFrame(cumplimiento_data)
    fig_cumplimiento = px.bar(
        df_cumplimiento,
        x='Etapa',
        y='Cumplimiento',
        title='Porcentaje de Cumplimiento por Etapa del Proceso',
        color='Cumplimiento',
        color_continuous_scale=['red', 'yellow', 'green']
    )
    fig_cumplimiento.add_hline(y=100, line_dash="dash", line_color="blue",
                               annotation_text="Objetivo 100%")
    st.plotly_chart(fig_cumplimiento, use_container_width=True)

# ---------------------------
# PÁGINA 5: SIMULACIÓN DE ESCENARIOS
# ---------------------------
elif pagina == "Simulación de Escenarios":
    st.markdown('<p class="main-header">🔮 Simulación de Escenarios</p>', unsafe_allow_html=True)

    st.markdown("### 🎯 Simule diferentes escenarios y vea el impacto en el cumplimiento")

    # Seleccionar etapa
    etapa_simulacion = st.selectbox(
        "Seleccione la etapa a simular:",
        list(variables_criticas.keys()),
        key="etapa_simulacion"
    )

    st.markdown(f"### 📌 Simulación para: {etapa_simulacion}")
    st.markdown("---")

    # Obtener datos base (guardados o por defecto)
    datos_base = {}
    if etapa_simulacion in st.session_state.datos_ingresados:
        datos_base = st.session_state.datos_ingresados[etapa_simulacion].copy()
    else:
        for var_nombre, var_data in variables_criticas[etapa_simulacion].items():
            datos_base[var_nombre] = var_data['actual']

    # Mostrar valores actuales
    st.markdown("#### 📊 Valores Actuales:")
    col1, col2 = st.columns(2)

    valores_actuales_display = {}
    with col1:
        for i, (var_nombre, var_data) in enumerate(variables_criticas[etapa_simulacion].items()):
            if i % 2 == 0:
                valor_actual = datos_base.get(var_nombre, var_data['actual'])
                st.metric(
                    var_nombre,
                    f"{valor_actual:.2f} {var_data['unidad']}",
                    f"Objetivo: {var_data['objetivo']} {var_data['unidad']}"
                )
                valores_actuales_display[var_nombre] = valor_actual

    with col2:
        for i, (var_nombre, var_data) in enumerate(variables_criticas[etapa_simulacion].items()):
            if i % 2 == 1:
                valor_actual = datos_base.get(var_nombre, var_data['actual'])
                st.metric(
                    var_nombre,
                    f"{valor_actual:.2f} {var_data['unidad']}",
                    f"Objetivo: {var_data['objetivo']} {var_data['unidad']}"
                )
                valores_actuales_display[var_nombre] = valor_actual

    st.markdown("---")

    # Formulario de simulación
    st.markdown("#### 🔮 Ingrese valores para simular:")

    cambios_simulacion = {}
    col1, col2 = st.columns(2)

    with col1:
        for i, (var_nombre, var_data) in enumerate(variables_criticas[etapa_simulacion].items()):
            if i % 2 == 0:
                valor_base = datos_base.get(var_nombre, var_data['actual'])
                nuevo_valor = st.number_input(
                    f"Simular {var_nombre}",
                    min_value=0.0,
                    value=float(valor_base),
                    step=0.1,
                    key=f"sim_{etapa_simulacion}_{var_nombre}",
                    help=f"Actual: {valor_base:.2f} | Objetivo: {var_data['objetivo']:.2f}"
                )
                cambios_simulacion[var_nombre] = nuevo_valor

    with col2:
        for i, (var_nombre, var_data) in enumerate(variables_criticas[etapa_simulacion].items()):
            if i % 2 == 1:
                valor_base = datos_base.get(var_nombre, var_data['actual'])
                nuevo_valor = st.number_input(
                    f"Simular {var_nombre}",
                    min_value=0.0,
                    value=float(valor_base),
                    step=0.1,
                    key=f"sim_{etapa_simulacion}_{var_nombre}_2",
                    help=f"Actual: {valor_base:.2f} | Objetivo: {var_data['objetivo']:.2f}"
                )
                cambios_simulacion[var_nombre] = nuevo_valor

    # Si hay número impar de variables, agregar la última
    if len(variables_criticas[etapa_simulacion]) % 2 == 1:
        var_nombre = list(variables_criticas[etapa_simulacion].keys())[-1]
        var_data = variables_criticas[etapa_simulacion][var_nombre]
        if var_nombre not in cambios_simulacion:
            valor_base = datos_base.get(var_nombre, var_data['actual'])
            nuevo_valor = st.number_input(
                f"Simular {var_nombre}",
                min_value=0.0,
                value=float(valor_base),
                step=0.1,
                key=f"sim_{etapa_simulacion}_{var_nombre}_final",
                help=f"Actual: {valor_base:.2f} | Objetivo: {var_data['objetivo']:.2f}"
            )
            cambios_simulacion[var_nombre] = nuevo_valor

    if st.button("🚀 Ejecutar Simulación", type="primary"):
        st.session_state.simular = True

    st.markdown("---")

    # Mostrar resultados de simulación
    if st.session_state.get('simular', False):
        st.markdown("### 📈 Resultados de la Simulación")

        evaluaciones_sim = []
        cumplimientos_sim = []
        evaluaciones_actual = []
        cumplimientos_actual = []

        for var_nombre, var_data in variables_criticas[etapa_simulacion].items():
            valor_simulado = cambios_simulacion.get(var_nombre, datos_base.get(var_nombre, var_data['actual']))
            valor_objetivo = var_data['objetivo']
            tipo = determinar_tipo_variable(var_nombre)
            eval_sim = evaluar_variable(valor_simulado, valor_objetivo, tipo)

            valor_actual = datos_base.get(var_nombre, var_data['actual'])
            eval_actual = evaluar_variable(valor_actual, valor_objetivo, tipo)

            evaluaciones_sim.append({
                'variable': var_nombre,
                'valor_simulado': valor_simulado,
                'valor_actual': valor_actual,
                'objetivo': valor_objetivo,
                'unidad': var_data['unidad'],
                'evaluacion_sim': eval_sim,
                'evaluacion_actual': eval_actual
            })
            cumplimientos_sim.append(eval_sim['cumplimiento'])
            cumplimientos_actual.append(eval_actual['cumplimiento'])

        # Comparación actual vs simulado
        st.markdown("#### 📊 Comparación: Actual vs Simulado")

        df_comparacion = pd.DataFrame([
            {
                'Variable': e['variable'],
                'Cumplimiento Actual (%)': e['evaluacion_actual']['cumplimiento'],
                'Cumplimiento Simulado (%)': e['evaluacion_sim']['cumplimiento'],
                'Mejora': e['evaluacion_sim']['cumplimiento'] - e['evaluacion_actual']['cumplimiento']
            }
            for e in evaluaciones_sim
        ])

        # Gráfico comparativo
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name='Actual',
            x=df_comparacion['Variable'],
            y=df_comparacion['Cumplimiento Actual (%)']
        ))
        fig_comp.add_trace(go.Bar(
            name='Simulado',
            x=df_comparacion['Variable'],
            y=df_comparacion['Cumplimiento Simulado (%)']
        ))
        fig_comp.add_hline(y=100, line_dash="dash", line_color="red",
                          annotation_text="Objetivo 100%")
        fig_comp.update_layout(
            title='Comparación de Cumplimiento: Actual vs Simulado',
            xaxis_title='Variable',
            yaxis_title='Cumplimiento (%)',
            barmode='group',
            height=500
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        # Resumen de mejoras
        cumplimiento_promedio_actual = sum(cumplimientos_actual) / len(cumplimientos_actual)
        cumplimiento_promedio_sim = sum(cumplimientos_sim) / len(cumplimientos_sim)
        mejora_promedio = cumplimiento_promedio_sim - cumplimiento_promedio_actual

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Cumplimiento Actual", f"{cumplimiento_promedio_actual:.1f}%")

        with col2:
            st.metric("Cumplimiento Simulado", f"{cumplimiento_promedio_sim:.1f}%")

        with col3:
            st.metric("Mejora Proyectada", f"{mejora_promedio:+.1f}%",
                     delta=f"{mejora_promedio:+.1f} puntos porcentuales")

        # Tabla de cambios con recomendaciones por variable
        st.markdown("#### 📋 Detalle de Cambios por Variable")
        df_cambios = pd.DataFrame([
            {
                'Variable': e['variable'],
                'Valor Actual': f"{e['valor_actual']:.2f} {e['unidad']}",
                'Valor Simulado': f"{e['valor_simulado']:.2f} {e['unidad']}",
                'Objetivo': f"{e['objetivo']:.2f} {e['unidad']}",
                'Cumpl. Actual': f"{e['evaluacion_actual']['cumplimiento']:.1f}%",
                'Cumpl. Simulado': f"{e['evaluacion_sim']['cumplimiento']:.1f}%",
                'Mejora': f"{e['evaluacion_sim']['cumplimiento'] - e['evaluacion_actual']['cumplimiento']:+.1f}%"
            }
            for e in evaluaciones_sim
        ])
        st.dataframe(df_cambios, use_container_width=True, hide_index=True)

        # Mostrar recomendaciones agrupadas para el escenario
        st.markdown("#### ✅ Recomendaciones para implementar (según simulación)")
        acciones_agrupadas = []
        for e in evaluaciones_sim:
            recs = recomendar_acciones(e['variable'], e['evaluacion_sim'])
            acciones_agrupadas.extend(recs)
        acciones_unicas = list(dict.fromkeys(acciones_agrupadas))
        for a in acciones_unicas:
            st.markdown(f"- {a}")

        st.session_state.simular = False

# ---------------------------
# PÁGINA 6: ECONOMÍA CIRCULAR
# ---------------------------
elif pagina == "Economía Circular":
    st.markdown('<p class="main-header">♻️ Trazabilidad y Economía Circular del Cobre</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📦 Trazabilidad de Material")

        tab1, tab2 = st.tabs(["🔍 Buscar Lote", "➕ Registrar Nuevo Lote"])

        with tab1:
            st.markdown("#### Buscar Lote Existente")
            if st.session_state.lotes_registrados:
                lotes_disponibles = list(st.session_state.lotes_registrados.keys())
                lote_seleccionado = st.selectbox(
                    "Seleccione un lote:",
                    lotes_disponibles,
                    key="lote_buscar"
                )
                lote_buscar = st.text_input(
                    "O ingrese código de lote:",
                    value=lote_seleccionado,
                    key="lote_input_buscar"
                )
            else:
                lote_buscar = st.text_input(
                    "Ingrese código de lote:",
                    key="lote_input_buscar"
                )

            if st.button("🔍 Rastrear Lote", key="btn_rastrear"):
                if lote_buscar in st.session_state.lotes_registrados:
                    st.success(f"✅ Lote {lote_buscar} encontrado en el sistema")
                    trazabilidad = st.session_state.lotes_registrados[lote_buscar]
                    st.markdown("#### 📋 Información del Lote")
                    for key, value in trazabilidad.items():
                        st.write(f"**{key}:** {value}")
                else:
                    st.error(f"❌ Lote {lote_buscar} no encontrado en el sistema")
                    st.info("💡 Puede registrar un nuevo lote en la pestaña 'Registrar Nuevo Lote'")

        with tab2:
            st.markdown("#### Registrar Nuevo Lote")
            codigo_auto = generar_codigo_lote()
            col_gen, col_manual = st.columns(2)
            with col_gen:
                usar_auto = st.checkbox("Usar código automático", value=True, key="usar_codigo_auto")
            if usar_auto:
                codigo_lote = st.text_input(
                    "Código de Lote:",
                    value=codigo_auto,
                    key="codigo_lote_registro"
                )
            else:
                codigo_lote = st.text_input(
                    "Código de Lote:",
                    placeholder="Ej: LOTE-2024-1205",
                    key="codigo_lote_manual"
                )

            st.markdown("---")
            st.markdown("#### Información del Lote")

            origen = st.text_input("Origen:", placeholder="Ej: Mina Los Pelambres, Chile", key="origen_lote")
            tipo = st.text_input("Tipo de Material:", placeholder="Ej: Cobre electrolítico C12200", key="tipo_lote")

            col_rec, col_pur = st.columns(2)
            with col_rec:
                contenido_reciclado = st.number_input("Contenido Reciclado (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key="reciclado_lote")
            with col_pur:
                pureza = st.number_input("Pureza (%):", min_value=0.0, max_value=100.0, value=99.0, step=0.01, key="pureza_lote")

            fecha_ingreso = st.date_input("Fecha de Ingreso:", value=datetime.now().date(), key="fecha_lote")
            masa_total = st.number_input("Masa Total (kg):", min_value=0.0, value=1000.0, step=0.1, key="masa_lote")

            estado = st.selectbox(
                "Estado:",
                ["En proceso - Selección y Preparación",
                 "En proceso - Fabricación de tubos",
                 "En proceso - Limpieza Química",
                 "En proceso - Mecanizado",
                 "En proceso - Soldadura/Brazing",
                 "Completado",
                 "Almacenado"],
                key="estado_lote"
            )

            certificacion = st.text_input("Certificación:", placeholder="Ej: ASTM B75", key="cert_lote")

            if st.button("💾 Registrar Lote", type="primary", key="btn_registrar_lote"):
                if codigo_lote:
                    if codigo_lote in st.session_state.lotes_registrados:
                        st.warning(f"⚠️ El lote {codigo_lote} ya existe. Se actualizará la información.")
                    st.session_state.lotes_registrados[codigo_lote] = {
                        'Origen': origen if origen else 'No especificado',
                        'Tipo': tipo if tipo else 'No especificado',
                        'Contenido reciclado': f'{contenido_reciclado:.1f}%',
                        'Pureza': f'{pureza:.2f}%',
                        'Fecha ingreso': fecha_ingreso.strftime('%Y-%m-%d'),
                        'Masa total': f'{masa_total:,.1f} kg',
                        'Estado': estado,
                        'Certificación': certificacion if certificacion else 'No especificada'
                    }
                    st.success(f"✅ Lote {codigo_lote} registrado exitosamente")
                    st.info(f"📝 Puede buscar este lote usando el código: **{codigo_lote}**")
                    st.rerun()
                else:
                    st.error("❌ Por favor ingrese un código de lote")

        # Mostrar resumen de lotes registrados
        if st.session_state.lotes_registrados:
            st.markdown("---")
            st.markdown(f"#### 📊 Resumen: {len(st.session_state.lotes_registrados)} lote(s) registrado(s)")
            with st.expander("Ver todos los lotes registrados"):
                for codigo, info in st.session_state.lotes_registrados.items():
                    st.markdown(f"**{codigo}** - {info['Estado']} - {info['Masa total']}")

    with col2:
        st.markdown("### 🔄 Ciclo de Vida del Material")

        fig_flujo = go.Figure(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=["Cobre Primario", "Cobre Reciclado", "Fabricación",
                       "Intercambiador", "Uso (15 años)", "Fin de Vida",
                       "Reciclaje", "Vertedero"],
                color=["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728",
                       "#9467bd", "#8c564b", "#2ca02c", "#7f7f7f"]
            ),
            link=dict(
                source=[0, 1, 2, 3, 4, 4, 5, 6],
                target=[2, 2, 3, 4, 5, 5, 6, 2],
                value=[58, 42, 100, 100, 100, 5, 95, 85]
            )
        ))
        fig_flujo.update_layout(title_text="Flujo de Material (kg)", font_size=10)
        st.plotly_chart(fig_flujo, use_container_width=True)

    st.markdown("---")

    # Indicadores de economía circular
    st.markdown("### 📊 Indicadores de Circularidad")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Tasa de Recuperación", "92%", "+3%")
        st.metric("Material Reciclado en Producto", "38%", "+5%")

    with col2:
        st.metric("Vida Útil Promedio", "15 años", "")
        st.metric("Tasa de Reciclaje al Fin de Vida", "95%", "")

    with col3:
        st.metric("Reducción Huella de Carbono", "35%", "+8%")
        st.metric("Ahorro de Energía vs Primario", "85%", "")

# ---------------------------
# PÁGINA 7: ODS Y CUMPLIMIENTO
# ---------------------------
elif pagina == "ODS y Cumplimiento":
    st.markdown('<p class="main-header">🎯 Objetivos de Desarrollo Sostenible</p>', unsafe_allow_html=True)

    st.markdown("### 🌍 ODS Relacionados con el Proyecto")

    for ods, data in ods_relacionados.items():
        col1, col2, col3 = st.columns([2, 3, 1])

        with col1:
            st.markdown(f"**{ods}**")

        with col2:
            st.markdown(f"*{data['nombre']}*")
            st.progress(data['cumplimiento'] / 100)

        with col3:
            st.metric("", f"{data['cumplimiento']}%")

        st.markdown("---")

    # Gráfico radar de ODS
    st.markdown("### 📊 Perfil de Cumplimiento ODS")

    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(
        r=[data['cumplimiento'] for data in ods_relacionados.values()],
        theta=[data['nombre'] for data in ods_relacionados.values()],
        fill='toself',
        name='Cumplimiento Actual'
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True
    )

    st.plotly_chart(fig_radar, use_container_width=True)

    # Metas específicas
    st.markdown("### 🎯 Metas Específicas por ODS")

    metas = {
        'ODS 6': [
            '✅ Reducir consumo de agua en 20% para 2025',
            '🔄 Reutilizar 50% del agua de proceso',
            '⚠️ Eliminar metales pesados en efluentes'
        ],
        'ODS 12': [
            '✅ Alcanzar 50% de material reciclado',
            '🔄 Reducir residuos peligrosos en 30%',
            '✅ Implementar sistema de trazabilidad completo'
        ],
        'ODS 13': [
            '✅ Reducir emisiones CO₂ en 25%',
            '🔄 Optimizar eficiencia energética en molienda',
            '⚠️ Compensar huella de carbono residual'
        ]
    }

    ods_seleccionado = st.selectbox("Seleccione ODS:", list(metas.keys()))

    for meta in metas[ods_seleccionado]:
        st.markdown(f"- {meta}")

# ---------------------------
# PÁGINA 8: GESTIÓN DE RESIDUOS
# ---------------------------
elif pagina == "Gestión de Residuos":
    st.markdown('<p class="main-header">🗑️ Gestión de Residuos Peligrosos</p>', unsafe_allow_html=True)

    st.markdown("### ⚠️ Residuos Peligrosos según D.S. 148")

    residuos = {
        'Ácidos agotados': {'cantidad': 65, 'unidad': 'L', 'codigo': 'A3090', 'peligrosidad': 'Alta'},
        'Fluidos de corte usados': {'cantidad': 80, 'unidad': 'L', 'codigo': 'Y9', 'peligrosidad': 'Media'},
        'Lodos con metales pesados': {'cantidad': 45, 'unidad': 'kg', 'codigo': 'A1180', 'peligrosidad': 'Alta'},
        'Solventes de limpieza': {'cantidad': 30, 'unidad': 'L', 'codigo': 'Y6', 'peligrosidad': 'Alta'},
        'Trapos contaminados': {'cantidad': 15, 'unidad': 'kg', 'codigo': 'Y18', 'peligrosidad': 'Media'}
    }

    for residuo, data in residuos.items():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        with col1:
            st.markdown(f"**{residuo}**")

        with col2:
            st.write(f"{data['cantidad']} {data['unidad']}")

        with col3:
            st.write(f"Código: {data['codigo']}")

        with col4:
            color_icon = "🔴" if data['peligrosidad'] == 'Alta' else "🟡"
            st.write(f"{color_icon} {data['peligrosidad']}")

        st.markdown("---")

    # Gráfico de generación de residuos
    st.markdown("### 📊 Tendencia de Generación de Residuos")

    fig_residuos = px.line(
        df_produccion.tail(90),
        x='fecha',
        y='residuos_peligrosos_kg',
        title='Residuos peligrosos generados (kg/día)'
    )
    st.plotly_chart(fig_residuos, use_container_width=True)

    # Plan de acción
    st.markdown("### 📋 Plan de Gestión de Residuos")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ✅ Acciones Implementadas")
        st.markdown("""
        - Sistema de segregación en origen
        - Almacenamiento temporal certificado
        - Transporte con empresa autorizada
        - Registro digital de movimientos
        """)

    with col2:
        st.markdown("#### 🔄 Próximas Acciones")
        st.markdown("""
        - Implementar reciclaje de fluidos de corte
        - Optimizar tratamiento de ácidos
        - Certificación ISO 14001
        - Reducir generación en 30%
        """)

# ---------------------------
# PÁGINA 9: REPORTES
# ---------------------------
elif pagina == "Reportes":
    st.markdown('<p class="main-header">📄 Generación de Reportes</p>', unsafe_allow_html=True)

    tipo_reporte = st.selectbox(
        "Tipo de reporte:",
        ["Reporte Mensual Ambiental", "Cumplimiento Normativo",
         "Indicadores de Circularidad", "Auditoria ODS"]
    )

    col1, col2 = st.columns(2)

    with col1:
        fecha_inicio = st.date_input("Fecha inicio:", datetime.now() - timedelta(days=30))

    with col2:
        fecha_fin = st.date_input("Fecha fin:", datetime.now())

    if st.button("📥 Generar Reporte", type="primary"):
        st.success("✅ Reporte generado exitosamente")

        st.markdown("### 📊 Vista Previa del Reporte")

        st.markdown(f"""
        **{tipo_reporte}**  
        Período: {fecha_inicio} - {fecha_fin}

        ---

        **Resumen Ejecutivo:**

        - ✅ Consumo energético: 9,850 kWh (-12% vs periodo anterior)
        - ✅ Consumo de agua: 98 m³ (-8% vs periodo anterior)
        - ⚠️ Residuos peligrosos: 1,950 kg (+5% vs periodo anterior)
        - ✅ Material reciclado: 38% (+5% vs periodo anterior)
        - ✅ Emisiones CO₂: 3.8 ton (-15% vs periodo anterior)

        **Cumplimiento Normativo:**
        - ASTM B75: ✅ Conforme
        - D.S. 148: ⚠️ 1 no conformidad menor
        - Ley REP 20.920: ✅ Conforme
        - ASME BPVC: ✅ Conforme

        **Recomendaciones:**
        1. Implementar sistema de neutralización de ácidos
        2. Aumentar porcentaje de cobre reciclado a 45%
        3. Optimizar consumo energético en etapa de molienda
        """)

        st.download_button(
            label="💾 Descargar Reporte PDF",
            data="Reporte en PDF (simulación)",
            file_name=f"reporte_{tipo_reporte.lower().replace(' ', '_')}.pdf",
            mime="application/pdf"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🌱 Sistema de Gestión Ambiental | Universidad Tecnológica Metropolitana | 2024</p>
    <p>Ingeniería Ambiental - Sección 411</p>
</div>

""", unsafe_allow_html=True)
