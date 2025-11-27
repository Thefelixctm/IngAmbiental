import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Gestión Ambiental - Intercambiadores de Calor",
    page_icon="♻️",
    layout="wide"
)

# Estilo CSS personalizado
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
</style>
""", unsafe_allow_html=True)

# Inicializar datos de ejemplo
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

# Variables críticas por etapa del proceso
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

# ODS relacionados
ods_relacionados = {
    'ODS 6': {'nombre': 'Agua Limpia y Saneamiento', 'cumplimiento': 72},
    'ODS 7': {'nombre': 'Energía Asequible y No Contaminante', 'cumplimiento': 68},
    'ODS 9': {'nombre': 'Industria, Innovación e Infraestructura', 'cumplimiento': 85},
    'ODS 12': {'nombre': 'Producción y Consumo Responsables', 'cumplimiento': 75},
    'ODS 13': {'nombre': 'Acción por el Clima', 'cumplimiento': 70}
}

# Sidebar - Navegación
st.sidebar.title("📊 Navegación")
pagina = st.sidebar.selectbox(
    "Seleccione módulo:",
    ["Dashboard Principal", "Variables Críticas", "Economía Circular", 
     "ODS y Cumplimiento", "Gestión de Residuos", "Reportes"]
)

# PÁGINA 1: DASHBOARD PRINCIPAL
if pagina == "Dashboard Principal":
    st.markdown('<p class="main-header">♻️ Sistema de Gestión Ambiental - Intercambiadores de Calor de Cobre</p>', unsafe_allow_html=True)
    
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
    
    # Alertas ambientales
    st.markdown("### 🚨 Alertas Ambientales Activas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="alert-critical">⚠️ CRÍTICO: Metales pesados en efluente superan límite (15 mg/L > 10 mg/L)</div>', unsafe_allow_html=True)
        st.markdown('<div class="alert-warning">⚡ ADVERTENCIA: Consumo energético cerca del límite mensual</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="alert-warning">♻️ ADVERTENCIA: Porcentaje de cobre reciclado bajo objetivo (38% < 50%)</div>', unsafe_allow_html=True)

# PÁGINA 2: VARIABLES CRÍTICAS
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
            progreso = (var_data['actual'] / var_data['objetivo']) * 100
            color = "green" if progreso <= 100 else "red" if progreso > 120 else "orange"
            st.progress(min(progreso / 100, 1.0))
        
        with col2:
            st.metric("Actual", f"{var_data['actual']} {var_data['unidad']}")
        
        with col3:
            st.metric("Objetivo", f"{var_data['objetivo']} {var_data['unidad']}")
        
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
                cumplimiento_total += (var_data['objetivo'] / var_data['actual']) * 100
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

# PÁGINA 3: ECONOMÍA CIRCULAR
elif pagina == "Economía Circular":
    st.markdown('<p class="main-header">♻️ Trazabilidad y Economía Circular del Cobre</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 Trazabilidad de Material")
        
        lote = st.text_input("Código de Lote:", "LOTE-2024-1205")
        
        if st.button("🔍 Rastrear Lote"):
            st.success("✅ Lote encontrado en el sistema")
            
            trazabilidad = {
                'Origen': 'Mina Los Pelambres, Chile',
                'Tipo': 'Cobre electrolítico C12200',
                'Contenido reciclado': '42%',
                'Pureza': '99.95%',
                'Fecha ingreso': '2024-11-15',
                'Masa total': '1,250 kg',
                'Estado': 'En proceso - Fabricación de tubos',
                'Certificación': 'ASTM B75 ✓'
            }
            
            for key, value in trazabilidad.items():
                st.write(f"**{key}:** {value}")
    
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

# PÁGINA 4: ODS Y CUMPLIMIENTO
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

# PÁGINA 5: GESTIÓN DE RESIDUOS
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
            color = "🔴" if data['peligrosidad'] == 'Alta' else "🟡"
            st.write(f"{color} {data['peligrosidad']}")
        
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

# PÁGINA 6: REPORTES
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