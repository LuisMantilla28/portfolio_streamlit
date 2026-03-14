import streamlit as st
import navigation
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import streamlit as st

DB_PATH="data/banking_risk.duckdb"
navigation.show()

st.title("SQL 🛢")
layout="wide"

st.markdown("---")

# ============================================================
# 1. Contextualización de los datos
# ============================================================

st.header("1. Contextualización de los datos")

st.write("""
El análisis se desarrolla sobre un **dataset bancario sintético (2022–2025)** diseñado para simular el funcionamiento integral de una cartera de crédito y su actividad transaccional. No se trata de datos aleatorios: las variables están estructuradas bajo una lógica económica coherente:

**Ingreso → Score → Tasa → Probabilidad de Incumplimiento (PD) → Mora**

El modelo sigue una estructura relacional típica de sistemas financieros reales.
""")

st.markdown("---")

st.subheader("Modelo relacional del dataset")

st.image(
    "assets/diagrma_sql_portafolio.png",
)

st.caption(
    "Esquema relacional del modelo. Las flechas representan relaciones por llave foránea (la linea continua significa que la llave clave hija depende de la tabla padre)."
)

st.markdown("---")



# ============================================================
# 2. Preguntas de interés
# ============================================================

st.header("2. Preguntas de interés")

st.write(
    """
Las siguientes preguntas guían el análisis y están diseñadas para demostraciones prácticas de:
**joins multi-tabla**, **agregaciones**, **funciones de ventana**, **análisis temporal** y **métricas comparables**.
"""
)

st.markdown("### 2.1 ¿Cómo evoluciona la mora a lo largo de las cuotas?")
st.write("""
Analizamos cómo cambia la mora a medida que avanza el número de cuota.
En particular, se calcula la **proporción de cuotas con atraso** (`days_late > 0`)
y el **promedio de días de mora** por número de cuota.
""")

# ------------------------------------------------
# Consulta SQL
# ------------------------------------------------
q = """select 
    installment_n, 
    avg(days_late) as promedio_dias_mora, 
    avg(case when days_late > 0 then 1 else 0 end) as proporcion_mora
from payments
group by installment_n
order by installment_n asc;
"""

with st.expander("Ver consulta SQL"):
    st.code(q, language="sql")

# ------------------------------------------------
# Ejecutar consulta
# ------------------------------------------------
con = duckdb.connect(DB_PATH)
df_mora = con.execute(q).df()
con.close()

# ------------------------------------------------
# Tabla de resultados (desplegable)
# ------------------------------------------------
with st.expander("Ver tabla de resultados"):
    st.dataframe(df_mora, use_container_width=True)

# ------------------------------------------------
# Gráfica
# ------------------------------------------------
x = df_mora["installment_n"].to_numpy()
y = df_mora["proporcion_mora"].to_numpy()

fig_mora_cuota, ax = plt.subplots(figsize=(10, 5), dpi=130)

ax.plot(x, y, marker="o", linewidth=2, markersize=5)
ax.set_title("Proporción de mora por cuota", pad=12)
ax.set_xlabel("Número de cuota")
ax.set_ylabel("Proporción en mora")

ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
ax.grid(True, which="major", alpha=0.25)

ax.set_xlim(x.min(), x.max())
ax.set_ylim(0, min(1, y.max() * 1.15))

plt.tight_layout()

st.markdown("### Visualización")
st.pyplot(fig_mora_cuota, use_container_width=True)

st.write("""
**Lectura inicial:** la proporción de mora muestra variaciones moderadas entre cuotas,
con niveles relativamente estables alrededor del 12%–15%, y un ligero aumento hacia
las cuotas intermedias.
""")



# ============================================================
# 2.2 Riesgo observado vs riesgo asignado por segmento
# ============================================================

st.markdown("### 2.2 ¿Qué segmento tiene mayor riesgo observado vs riesgo asignado?")
st.markdown("""
**🎯 Pregunta**  
¿La **PD latente asignada** (`pd_latent`) coincide con la mora observada por `segment`?  
*(Ejemplo: comparar PD promedio vs tasa real de mora observada por segmento.)*
""")

st.markdown("#### Consulta SQL")

q_segmento = """
SELECT 
    segment,
    AVG(pd_latent) AS promedio_estimado,
    AVG(CASE WHEN days_late > 0 THEN 1 ELSE 0 END) AS prop_retardos
FROM payments
LEFT JOIN loans
    ON payments.loan_id = loans.loan_id
JOIN customers
    ON customers.customer_id = payments.customer_id
GROUP BY segment
ORDER BY segment;
"""

st.code(q_segmento, language="sql")

# ------------------------------------------------
# Ejecutar consulta
# ------------------------------------------------
con = duckdb.connect(DB_PATH)
df_comparacion_mora = con.execute(q_segmento).df()
con.close()

# ------------------------------------------------
# Resultados contraídos
# ------------------------------------------------
with st.expander("Ver resultados"):

    st.markdown("#### Tabla de resultados")
    st.dataframe(df_comparacion_mora, use_container_width=True)

    # ------------------------------------------------
    # Gráfica
    # ------------------------------------------------
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib.ticker as mtick

    segmentos = df_comparacion_mora["segment"]
    estimado = df_comparacion_mora["promedio_estimado"]
    observado = df_comparacion_mora["prop_retardos"]

    x = np.arange(len(segmentos))
    width = 0.35

    fig_riesgo_segmento, ax = plt.subplots(figsize=(8, 5), dpi=130)

    ax.bar(x - width/2, estimado, width, label="PD asignada")
    ax.bar(x + width/2, observado, width, label="Mora observada")

    ax.set_xticks(x)
    ax.set_xticklabels(segmentos)
    ax.set_ylabel("Proporción")
    ax.set_title("Riesgo asignado vs mora observada por segmento", pad=12)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.legend()
    ax.grid(True, axis="y", alpha=0.25)

    plt.tight_layout()

    st.markdown("#### Visualización")
    st.pyplot(fig_riesgo_segmento, use_container_width=True)

    st.markdown("""
**Interpretación inicial**

- El segmento **Mass** presenta la mayor mora observada y también una PD promedio relativamente alta.  
- El segmento **Affluent** muestra una mora observada menor que la del segmento Mass, en línea con un menor riesgo relativo.  
- El segmento **SME** presenta una PD asignada intermedia, pero una mora observada más baja que la esperada.  

En conjunto, la **PD latente asignada captura razonablemente el orden relativo del riesgo entre segmentos**,
aunque existen diferencias entre el riesgo teórico y el comportamiento efectivamente observado.
""")
    
# ============================================================
# 2.3 Relación entre ingreso y mora
# ============================================================

st.markdown("### 2.3 ¿Existe relación entre ingreso y mora?")
st.markdown("""
**🎯 Pregunta**  
¿Los clientes con menor `income_monthly` presentan mayor probabilidad de atraso?  
*(Ejemplo: mora por rangos de ingreso.)*
""")

st.markdown("#### Consulta SQL")

q_ingreso_mora = """
SELECT 
    CASE 
        WHEN income_monthly < 2000000 THEN 'Bajo (menor a 2M)'
        WHEN income_monthly < 10000000 THEN 'Medio (entre 2M y 10M)'
        ELSE 'Alto (más de 10M)'
    END AS grupo_ingresos,
    AVG(CASE WHEN days_late > 0 THEN 1 ELSE 0 END) AS proporcion_retrasos
FROM customers
JOIN payments 
    ON customers.customer_id = payments.customer_id
GROUP BY grupo_ingresos
ORDER BY 
    CASE 
        WHEN grupo_ingresos = 'Bajo (menor a 2M)' THEN 1
        WHEN grupo_ingresos = 'Medio (entre 2M y 10M)' THEN 2
        ELSE 3
    END;
"""

st.code(q_ingreso_mora, language="sql")

# ------------------------------------------------
# Ejecutar consulta
# ------------------------------------------------
con = duckdb.connect(DB_PATH)
df_ingreso_mora = con.execute(q_ingreso_mora).df()
con.close()

# ------------------------------------------------
# Resultados contraídos
# ------------------------------------------------
with st.expander("Ver resultados"):

    st.markdown("#### Tabla de resultados")
    st.dataframe(df_ingreso_mora, use_container_width=True)

    # ------------------------------------------------
    # Gráfica
    # ------------------------------------------------
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick

    x = df_ingreso_mora["grupo_ingresos"]
    y = df_ingreso_mora["proporcion_retrasos"]

    fig_ingreso_mora, ax = plt.subplots(figsize=(8, 5), dpi=130)

    ax.bar(x, y)
    ax.set_title("Proporción de mora por rango de ingreso", pad=12)
    ax.set_xlabel("Grupo de ingresos")
    ax.set_ylabel("Proporción de retrasos")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.grid(True, axis="y", alpha=0.25)

    plt.xticks(rotation=10)
    plt.tight_layout()

    st.markdown("#### Visualización")
    st.pyplot(fig_ingreso_mora, use_container_width=True)

    st.markdown("""
**Interpretación inicial**

- Los clientes del grupo **Bajo (menor a 2M)** presentan la mayor proporción de retrasos, con un valor cercano al **14.3%**.  
- El grupo **Medio (entre 2M y 10M)** muestra una proporción intermedia, alrededor de **13.1%**.  
- El grupo **Alto (más de 10M)** registra la menor mora observada, con aproximadamente **11.6%**.  

En conjunto, los resultados sugieren una **relación inversa entre ingreso y mora**:
a mayor ingreso mensual, menor probabilidad de atraso en los pagos.
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
    """)

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
- `installment_n` → Número de cuota.  
- `due_date` → Fecha de vencimiento.  
    """)

with col2:
    st.markdown(""" 
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
- `due_date` → Fecha de vencimiento.  
    """)

with col2:
    st.markdown("""
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


