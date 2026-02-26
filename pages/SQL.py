import streamlit as st
import navigation

navigation.show()

st.title("SQL")
st.caption("Relational data modeling and analytical SQL exploration")

st.markdown("---")

# ============================================================
# 1. Contextualización de los datos
# ============================================================

st.header("1. Contextualización de los datos")

st.write("""
El análisis se desarrolla sobre un **dataset bancario sintético (2022–2025)** diseñado para simular el funcionamiento integral de una cartera de crédito y su actividad transaccional.

No se trata de datos aleatorios: las variables están estructuradas bajo una lógica económica coherente:

**Ingreso → Score → Tasa → Probabilidad de Incumplimiento (PD) → Mora**

El modelo sigue una estructura relacional típica de sistemas financieros reales.
""")

st.markdown("---")

st.subheader("Modelo relacional del dataset")

st.image(
    "assets/diagrma_sql_portafolio.png",
    use_container_width=True,
)

st.caption(
    "Esquema relacional del modelo. Las flechas representan relaciones por llave foránea (la linea continua significa que la llave clave hija depende de la tabla padre)."
)

st.markdown("---")


# ============================================================
# Customers
# ============================================================

st.subheader("1️⃣ Customers (1.000 registros)")
st.write("Dimensión principal de clientes (información demográfica y financiera básica).")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
- `customer_id` → Identificador único del cliente (PK).  
- `segment` → Segmento comercial.  
- `region` → Región geográfica asociada.  
- `age` → Edad del cliente.
    """)

with col2:
    st.markdown("""
- `income_monthly` → Ingreso mensual estimado (COP).  
- `risk_score` → Score crediticio.  
- `customer_since` → Fecha de vinculación.
    """)

st.markdown("---")

# ============================================================
# Accounts
# ============================================================

st.subheader("2️⃣ Accounts (1.300 registros)")
st.write("Productos de depósito asociados a clientes.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
- `account_id` → Identificador único (PK).  
- `customer_id` → FK hacia Customers.  
- `account_type` → Tipo de cuenta.
    """)

with col2:
    st.markdown("""
- `opened_date` → Fecha de apertura.  
- `status` → Estado de la cuenta.
    """)

st.markdown("---")

# ============================================================
# Loans
# ============================================================

st.subheader("3️⃣ Loans (1.100 registros)")
st.write("Cartera de créditos originados.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
- `loan_id` → Identificador único (PK).  
- `customer_id` → FK hacia Customers.  
- `product` → Tipo de producto.  
- `origination_date` → Fecha de desembolso.  
- `amount` → Monto del crédito.
    """)

with col2:
    st.markdown("""
- `term_months` → Plazo en meses.  
- `interest_rate` → Tasa anual.  
- `pd_latent` → Probabilidad de incumplimiento.  
- `segment` → Segmento del cliente.  
- `risk_score` → Score del cliente.  
- `income_monthly` → Ingreso mensual.
    """)

st.markdown("Nota: Algunas variables se replican desde Customers para facilitar consultas analíticas.")

st.markdown("---")

# ============================================================
# Payments
# ============================================================

st.subheader("4️⃣ Payments (13.200 registros)")
st.write("Calendario de cuotas por préstamo.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
- `payment_id` → Identificador único (PK).  
- `loan_id` → FK hacia Loans.  
- `customer_id` → FK hacia Customers.  
- `origination_date` → Fecha de originación.  
- `amount` → Monto del crédito.  
- `interest_rate` → Tasa anual.
    """)

with col2:
    st.markdown("""
- `pd_latent` → PD latente.  
- `installment_n` → Número de cuota.  
- `due_date` → Fecha de vencimiento.  
- `amount_due` → Valor esperado.  
- `paid_flag` → Indicador de pago.  
- `days_late` → Días de atraso.  
- `paid_date` → Fecha de pago.  
- `paid_amount` → Monto pagado.
    """)

st.markdown("---")

# ============================================================
# Delinquency
# ============================================================

st.subheader("5️⃣ Delinquency (13.200 registros)")
st.write("Clasificación de mora por cuota.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
- `loan_id` → FK hacia Loans.  
- `customer_id` → FK hacia Customers.  
- `installment_n` → Número de cuota.
    """)

with col2:
    st.markdown("""
- `due_date` → Fecha de vencimiento.  
- `paid_date` → Fecha de pago.  
- `days_past_due` → Días de mora.  
- `delinquency_status` → Bucket regulatorio.
    """)

st.markdown("**Llave primaria:** (`loan_id`, `installment_n`)")

st.markdown("---")

# ============================================================
# Transactions
# ============================================================

st.subheader("6️⃣ Transactions (10.000 registros)")
st.write("Actividad transaccional de clientes.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
- `tx_id` → Identificador único (PK).  
- `tx_date` → Fecha de transacción.
    """)

with col2:
    st.markdown("""
- `customer_id` → FK hacia Customers.  
- `tx_type` → Tipo de transacción.  
- `amount` → Monto transaccionado.
    """)
st.markdown("---")

st.success("""
El tamaño del dataset permite practicar consultas SQL reales: joins multi-tabla, agregaciones, ventanas,
análisis temporal y construcción de métricas a nivel cliente, crédito y cuota.
""")

# ============================================================
# Secciones siguientes (placeholders)
# ============================================================

# ============================================================
# 2. Preguntas de interés
# ============================================================

st.markdown("---")
st.header("2. Preguntas de interés")

st.write(
    """
Las siguientes preguntas guían el análisis y están diseñadas para demostraciones prácticas de:
**joins multi-tabla**, **agregaciones**, **funciones de ventana**, **análisis temporal** y **métricas comparables**.
"""
)

st.markdown("### 2.1 ¿Cómo evoluciona la mora a lo largo de las cuotas?")
st.markdown("""
**🎯 Pregunta**  
¿La probabilidad de atraso aumenta o disminuye conforme avanza el número de cuota (`installment_n`)?  
*(Ejemplo de salida esperada: curva de mora por número de cuota, y comparación por producto/segmento.)*
""")

st.markdown("### 2.2 ¿Qué segmento tiene mayor riesgo observado vs riesgo asignado?")
st.markdown("""
**🎯 Pregunta**  
¿La **PD latente asignada** (`pd_latent`) coincide con la mora observada por `segment`?  
*(Ejemplo: comparar PD promedio vs tasa real de mora 30+ / 90+ por segmento.)*
""")

st.markdown("### 2.3 ¿Existe relación entre ingreso y mora?")
st.markdown("""
**🎯 Pregunta**  
¿Los clientes con menor `income_monthly` presentan mayor probabilidad de atraso?  
*(Ejemplo: mora por deciles de ingreso y/o por rangos de ingreso.)*
""")

st.markdown("### 2.4 ¿Qué producto es más riesgoso?")
st.markdown("""
**🎯 Pregunta**  
¿Cuál tipo de crédito (`product`) presenta mayor tasa de mora severa (**90+**)?
*(Ejemplo: ranking de productos por % de cuotas 90+ o por % de créditos con al menos una cuota 90+.)*
""")

st.markdown("### 2.5 ¿El comportamiento transaccional está asociado a menor riesgo?")
st.markdown("""
**🎯 Pregunta**  
¿Clientes con mayor actividad transaccional (número de transacciones y/o monto total) presentan menor mora?  
*(Ejemplo: comparar mora entre cuantiles de actividad transaccional.)*
""")

st.info(
    "En la siguiente sección se implementarán consultas SQL y gráficas para responder estas preguntas "
    "con indicadores y visualizaciones claras."
)

st.markdown("---")
st.header("3. Consultas y gráficas")
st.caption("Próximamente")
