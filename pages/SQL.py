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

# ============================================================
# Customers
# ============================================================

st.subheader("1️⃣ Customers (30.000 registros)")

st.write("Dimensión principal de clientes.")

st.markdown("""
**Columnas:**

- `customer_id` → Identificador único del cliente.  
- `segment` → Segmento comercial (Mass, Affluent, SME).  
- `region` → Región geográfica en Colombia.  
- `age` → Edad del cliente (18–75 años).  
- `income_monthly` → Ingreso mensual estimado (distribución lognormal).  
- `risk_score` → Score crediticio (300–850), correlacionado con ingreso y edad.  
- `customer_since` → Fecha de vinculación al banco.
""")

st.markdown("---")

# ============================================================
# Accounts
# ============================================================

st.subheader("2️⃣ Accounts (40.000 registros)")

st.write("Productos de depósito asociados a clientes.")

st.markdown("""
**Columnas:**

- `account_id` → Identificador único de la cuenta.  
- `customer_id` → Cliente titular de la cuenta.  
- `account_type` → Tipo de cuenta (Savings / Checking).  
- `opened_date` → Fecha de apertura.  
- `status` → Estado de la cuenta (Active, Dormant, Closed).
""")

st.markdown("---")

# ============================================================
# Loans
# ============================================================

st.subheader("3️⃣ Loans (35.000 registros)")

st.write("Cartera de créditos originados entre 2022 y 2025.")

st.markdown("""
**Columnas:**

- `loan_id` → Identificador único del crédito.  
- `customer_id` → Cliente asociado al préstamo.  
- `product` → Tipo de producto (Consumo, Libranza, Hipotecario, Vehículo, Tarjeta).  
- `origination_date` → Fecha de desembolso.  
- `amount` → Monto desembolsado (colas pesadas por tipo de producto).  
- `term_months` → Plazo contractual del crédito.  
- `interest_rate` → Tasa de interés anual, dependiente del producto y del score.  
- `pd_latent` → Probabilidad de incumplimiento latente (simulada).  
- `segment` → Segmento del cliente al momento de originación.  
- `risk_score` → Score del cliente al originar el crédito.  
- `income_monthly` → Ingreso mensual del cliente.
""")

st.markdown("""
La tasa de interés aumenta cuando el score es bajo, replicando la lógica de pricing por riesgo.
""")

st.markdown("---")

# ============================================================
# Payments
# ============================================================

st.subheader("4️⃣ Payments (~840.000 registros)")

st.write("Calendario de cuotas generado por préstamo (hasta 24 cuotas por crédito).")

st.markdown("""
**Columnas:**

- `payment_id` → Identificador único de la cuota.  
- `loan_id` → Crédito asociado.  
- `customer_id` → Cliente asociado.  
- `installment_n` → Número de cuota.  
- `due_date` → Fecha de vencimiento.  
- `amount_due` → Valor esperado de la cuota.  
- `paid_flag` → Indicador binario (1 = pagada, 0 = no pagada).  
- `days_late` → Días de atraso.  
- `paid_date` → Fecha efectiva de pago (si aplica).  
- `paid_amount` → Monto efectivamente pagado.
""")

st.markdown("""
El atraso se simula en función de la PD latente del crédito.
""")

st.markdown("---")

# ============================================================
# Delinquency
# ============================================================

st.subheader("5️⃣ Delinquency (~840.000 registros)")

st.write("Clasificación regulatoria de mora por cuota.")

st.markdown("""
**Columnas:**

- `loan_id` → Crédito asociado.  
- `customer_id` → Cliente asociado.  
- `installment_n` → Número de cuota.  
- `due_date` → Fecha de vencimiento.  
- `paid_date` → Fecha de pago (si aplica).  
- `days_past_due` → Días efectivos de mora.  
- `delinquency_status` → Bucket regulatorio:
  - Current  
  - 1–29  
  - 30–59  
  - 60–89  
  - 90+  
  - Unpaid
""")

st.markdown("---")

# ============================================================
# Transactions
# ============================================================

st.subheader("6️⃣ Transactions (450.000 registros)")

st.write("Actividad transaccional de clientes entre 2022 y 2025.")

st.markdown("""
**Columnas:**

- `tx_id` → Identificador único de la transacción.  
- `tx_date` → Fecha de la transacción.  
- `customer_id` → Cliente asociado.  
- `tx_type` → Tipo de transacción (POS, Transfer, ATM, Online, BillPay).  
- `amount` → Monto transaccionado.
""")

st.markdown("""
La distribución de montos reproduce comportamiento realista:
muchas transacciones pequeñas y pocas de alto valor.
""")

st.markdown("---")

st.success("""
El volumen del dataset permite ejecutar joins complejos, agregaciones pesadas,
análisis temporal y métricas avanzadas de cartera usando SQL.
""")

# ============================================================
# Secciones siguientes (placeholders)
# ============================================================

st.markdown("---")
st.header("2. Preguntas de interés")
st.caption("Próximamente")

st.markdown("---")
st.header("3. Consultas y gráficas")
st.caption("Próximamente")
