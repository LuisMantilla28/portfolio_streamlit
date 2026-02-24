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

# ============================================================
# Customers
# ============================================================

st.subheader("1️⃣ Customers (1.000 registros)")
st.write("Dimensión principal de clientes (información demográfica y financiera básica).")

st.markdown("""
**Columnas:**

- `customer_id` → Identificador único del cliente (PK).  
- `segment` → Segmento comercial (p. ej., Mass / Affluent / SME).  
- `region` → Región geográfica asociada al cliente.  
- `age` → Edad del cliente.  
- `income_monthly` → Ingreso mensual estimado (COP).  
- `risk_score` → Score crediticio (entero), relacionado con el perfil financiero del cliente.  
- `customer_since` → Fecha de vinculación del cliente.
""")

st.markdown("---")

# ============================================================
# Accounts
# ============================================================

st.subheader("2️⃣ Accounts (1.300 registros)")
st.write("Productos de depósito asociados a clientes (relación many-to-one con Customers).")

st.markdown("""
**Columnas:**

- `account_id` → Identificador único de la cuenta (PK).  
- `customer_id` → Identificador del cliente titular (FK → `customers.customer_id`).  
- `account_type` → Tipo de cuenta (p. ej., Savings / Checking).  
- `opened_date` → Fecha de apertura de la cuenta.  
- `status` → Estado de la cuenta (p. ej., Active / Dormant / Closed).
""")

st.markdown("---")

# ============================================================
# Loans
# ============================================================

st.subheader("3️⃣ Loans (1.100 registros)")
st.write("Cartera de créditos originados (relación many-to-one con Customers).")

st.markdown("""
**Columnas:**

- `loan_id` → Identificador único del crédito (PK).  
- `customer_id` → Cliente asociado al préstamo (FK → `customers.customer_id`).  
- `product` → Tipo de producto (p. ej., Consumo, Libranza, Hipotecario, Vehículo, Tarjeta).  
- `origination_date` → Fecha de originación/desembolso del crédito.  
- `amount` → Monto desembolsado (COP).  
- `term_months` → Plazo del crédito en meses.  
- `interest_rate` → Tasa de interés anual (double).  
- `pd_latent` → Probabilidad de incumplimiento latente (double), usada para simular mora.  
- `segment` → Segmento del cliente (copiado desde Customers para consultas rápidas).  
- `risk_score` → Score del cliente (copiado desde Customers para consultas rápidas).  
- `income_monthly` → Ingreso mensual del cliente (copiado desde Customers para consultas rápidas).
""")

st.markdown("""
Nota: `segment`, `risk_score` e `income_monthly` aparecen también en Loans para facilitar análisis sin joins,
aunque la fuente original de esas variables es Customers.
""")

st.markdown("---")

# ============================================================
# Payments
# ============================================================

st.subheader("4️⃣ Payments (13.200 registros)")
st.write("Calendario de cuotas por préstamo (≈ 12 cuotas por crédito).")

st.markdown("""
**Columnas:**

- `payment_id` → Identificador único de la cuota (PK).  
- `loan_id` → Crédito asociado a la cuota (FK → `loans.loan_id`).  
- `customer_id` → Cliente asociado (FK → `customers.customer_id`).  
- `origination_date` → Fecha de originación del crédito (copiada para facilitar análisis temporal).  
- `amount` → Monto del crédito (copiado para facilitar análisis).  
- `interest_rate` → Tasa anual del crédito (copiada para facilitar análisis).  
- `pd_latent` → PD latente del crédito (copiada para facilitar análisis).  
- `installment_n` → Número de cuota (1, 2, 3, …).  
- `due_date` → Fecha de vencimiento.  
- `amount_due` → Valor esperado de la cuota (COP).  
- `paid_flag` → Indicador binario (1 = pagada, 0 = no pagada).  
- `days_late` → Días de atraso (0 si pagó a tiempo).  
- `paid_date` → Fecha efectiva de pago (NULL si no pagó).  
- `paid_amount` → Monto pagado (0 si no pagó).
""")

st.markdown("---")

# ============================================================
# Delinquency
# ============================================================

st.subheader("5️⃣ Delinquency (13.200 registros)")
st.write("Clasificación de mora por cuota (bucketización basada en días de mora).")

st.markdown("""
**Columnas:**

- `loan_id` → Crédito asociado (FK → `loans.loan_id`).  
- `customer_id` → Cliente asociado (FK → `customers.customer_id`).  
- `installment_n` → Número de cuota (parte de la PK compuesta).  
- `due_date` → Fecha de vencimiento.  
- `paid_date` → Fecha de pago (si aplica).  
- `days_past_due` → Días de mora (DPD).  
- `delinquency_status` → Bucket de mora (p. ej., Current, 1–29, 30–59, 60–89, 90+, Unpaid).  

**Llave primaria:** (`loan_id`, `installment_n`)
""")

st.markdown("---")

# ============================================================
# Transactions
# ============================================================

st.subheader("6️⃣ Transactions (10.000 registros)")
st.write("Actividad transaccional de clientes (movimientos de gasto/ingreso).")

st.markdown("""
**Columnas:**

- `tx_id` → Identificador único de la transacción (PK).  
- `tx_date` → Fecha de la transacción.  
- `customer_id` → Cliente asociado (FK → `customers.customer_id`).  
- `tx_type` → Tipo de transacción (p. ej., POS, Transfer, ATM, Online, BillPay).  
- `amount` → Monto transaccionado (COP).
""")

st.markdown("---")

st.success("""
El tamaño del dataset permite practicar consultas SQL reales: joins multi-tabla, agregaciones, ventanas,
análisis temporal y construcción de métricas a nivel cliente, crédito y cuota.
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
