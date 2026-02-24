import streamlit as st
import navigation

# Sidebar + estilos (compartido en todas las páginas)
navigation.show()

# -----------------------------
# Página: SQL
# -----------------------------
st.title("SQL")
st.caption("Portfolio section — SQL analytics and relational data exploration")

st.markdown("---")

# =============================
# 1) Contextualización de los datos
# =============================
st.header("1. Contextualización de los datos")

st.write(
    """
Este proyecto utiliza un **dataset bancario sintético** a escala realista (2022–2025), diseñado para simular
el funcionamiento de una cartera de crédito y un sistema transaccional.  
La idea no es generar datos al azar, sino un entorno **coherente** donde variables demográficas, financieras y de
comportamiento se relacionan de forma plausible, permitiendo practicar **consultas SQL avanzadas** y análisis analítico.
"""
)

st.subheader("Estructura del dataset (relacional)")

c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown("**Customers (30.000)**")
    st.write(
        """
- Clientes con variables demográficas y financieras  
- Segmento (Mass / Affluent / SME), región, edad, ingreso mensual  
- **Risk score (300–850)** relacionado con ingreso/edad (con ruido para realismo)
"""
    )

    st.markdown("**Loans (35.000)**")
    st.write(
        """
- Créditos por producto (consumo, libranza, hipotecario, vehículo, tarjeta)  
- Monto, plazo, **tasa anual** dependiente del producto y del score  
- **PD latente** dependiente del score (pricing por riesgo: score bajo → tasa mayor)
"""
    )

    st.markdown("**Delinquency (~840.000)**")
    st.write(
        """
- Clasificación de cada cuota en buckets: Current, 1–29, 30–59, 60–89, 90+, Unpaid  
- Útil para análisis de cartera y métricas estándar
"""
    )

with c2:
    st.markdown("**Accounts (40.000)**")
    st.write(
        """
- Cuentas de depósito asociadas a clientes  
- Tipo (Savings/Checking), estado (Active/Dormant/Closed), fecha de apertura  
- Permite analizar actividad y permanencia
"""
    )

    st.markdown("**Payments (~840.000)**")
    st.write(
        """
- Calendario de cuotas por préstamo (hasta 24 por crédito)  
- Vencimiento, monto esperado, flag de pago, días de atraso, fecha/monto pagado  
- Atraso e impago simulados según la **PD latente**
"""
    )

    st.markdown("**Transactions (450.000)**")
    st.write(
        """
- Actividad transaccional (POS, transferencias, ATM, online, pago facturas)  
- Montos con patrón realista: muchas transacciones pequeñas y pocas grandes  
- Permite estudiar señales previas al deterioro
"""
    )

st.subheader("Relación lógica entre variables (coherencia)")
st.write(
    """
El dataset preserva una estructura causal/plausible para análisis:
**Ingreso → Score → Tasa → PD → Mora**, además de comportamiento transaccional asociado al perfil del cliente.
"""
)

st.subheader("Escala")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Clientes", "30.000")
    st.metric("Cuentas", "40.000")
with m2:
    st.metric("Créditos", "35.000")
    st.metric("Transacciones", "450.000")
with m3:
    st.metric("Cuotas", "~840.000")
    st.metric("Registros mora", "~840.000")

st.info(
    "En las siguientes secciones se presentarán preguntas de interés y consultas SQL (con tablas y gráficas) "
    "para responderlas de forma clara."
)

# =============================
# 2) Preguntas de interés (placeholder)
# =============================
st.markdown("---")
st.header("2. Preguntas de interés")
st.caption("Próximamente: preguntas guía para el análisis SQL.")
st.write("")

# =============================
# 3) Consultas y gráficas (placeholder)
# =============================
st.markdown("---")
st.header("3. Consultas y gráficas")
st.caption("Próximamente: consultas SQL + visualizaciones que responden las preguntas de interés.")
st.write("")
