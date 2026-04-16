import streamlit as st
import navigation
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import streamlit as st

DB_PATH="data/banking_risk.duckdb"
navigation.show()
layout="wide"

st.title("SQL para Riesgo Bancario: Analítica Estratégica para Decisiones de Negocio")
st.markdown("""
Esta sección presenta un proyecto de analítica aplicada al riesgo bancario desarrollado con **SQL, DuckDB y visualización de datos**, con el propósito de convertir información operativa en decisiones estratégicas. La data utilizada en este caso fue generada a partir de una simulación propia, cuyo código puede consultarse en [este repositorio de GitHub](https://github.com/LuisMantilla28/portfolio_streamlit/blob/cb9e647f0872bc61642a9abd746525ca663ef5f3/Notebooks/Generador_data.ipynb). A partir de un ecosistema financiero sintético que integra clientes, préstamos, pagos y transacciones, el análisis se estructura como una historia de negocio que conecta **rentabilidad, calidad de cartera, comportamiento de pago y oportunidades comerciales**.

Más allá de describir métricas aisladas, la página busca mostrar una capacidad clave para roles en **riesgo, analítica y finanzas cuantitativas**: construir consultas que permitan diagnosticar el portafolio, detectar patrones relevantes y traducir hallazgos en recomendaciones accionables. El recorrido analítico parte de la composición de la cartera y su exposición por producto, profundiza en los indicadores de mora y en la relación entre ingreso y perfil de riesgo, incorpora señales tempranas desde el comportamiento transaccional y culmina con la identificación de un segmento objetivo de alto valor comercial.

En conjunto, esta página funciona como una demostración de portafolio orientada a entornos financieros reales, donde el uso de SQL no se limita a extraer datos, sino que se convierte en una herramienta para **entender el negocio, explicar el riesgo y apoyar la toma de decisiones basada en evidencia**.
""")

st.markdown("---")

# ============================================================
# 1. Contextualización de los datos
# ============================================================

st.header("1. Objetivo del análisis")

st.write("""
El propósito de esta página es evaluar la cartera de crédito desde una perspectiva de **riesgo, rentabilidad y oportunidad comercial**, utilizando consultas SQL sobre un entorno financiero sintético. En particular, el análisis busca responder:
1. Qué productos concentran mayor exposición
2. Cuáles presentan señales de deterioro en el pago
3. Qué variables parecen explicar mejor la mora 
4. Qué perfiles de clientes representan oportunidades atractivas de crecimiento con riesgo controlado.
""")

st.header("2. Datos utilizados")

st.write("""

El análisis se apoya en una base de datos financiera sintética con estructura relacional, cuyo código puede consultarse en [este repositorio de GitHub](https://github.com/LuisMantilla28/portfolio_streamlit/blob/cb9e647f0872bc61642a9abd746525ca663ef5f3/Notebooks/Generador_data.ipynb), diseñada para representar el ciclo de vida de un cliente dentro de una entidad bancaria: desde su caracterización inicial, pasando por la colocación de productos de crédito, hasta su comportamiento de pago y su actividad transaccional. La relación entre tablas permite estudiar el riesgo no como un fenómeno aislado, sino como el resultado de la interacción entre perfil financiero, endeudamiento, cumplimiento y uso de canales.

Las tablas principales son las siguientes:

- **customers**: contiene la información base de los clientes y funciona como eje central de segmentación del análisis. Incluye variables como segmento, región, ingreso mensual, score de riesgo y antigüedad, que permiten caracterizar el perfil financiero de cada persona y comparar comportamientos entre grupos.

- **loans**: registra los productos de crédito asociados a cada cliente. Esta tabla permite analizar la composición de la cartera, el capital colocado, los plazos, las tasas de interés y la distribución del portafolio por tipo de producto. Es la base para estudiar la relación entre exposición, rentabilidad esperada y riesgo crediticio.

- **payments**: almacena el detalle del comportamiento de pago de cada préstamo a nivel de cuota. Aquí se observan variables críticas como fecha pactada, fecha efectiva de pago, valor exigido, valor pagado y días de retraso. Esta tabla es fundamental para construir indicadores de mora, evaluar disciplina de pago y detectar deterioro en la calidad de la cartera.

- **transactions**: recoge la actividad transaccional de los clientes a través de distintos canales y tipos de operación. Su valor analítico radica en que permite complementar la visión tradicional del riesgo con señales de comportamiento financiero cotidiano, como intensidad de uso, preferencia por canales y montos movilizados. Esto resulta especialmente útil para identificar alertas tempranas de estrés financiero o cambios en la relación del cliente con la entidad.

La siguiente figura resume la estructura relacional del modelo de datos utilizado en esta página:
"""
)

st.image(
    "assets/diagrama_db.png",
)

st.markdown("A nivel analítico, cada tabla cumple un rol distinto dentro de la historia del negocio:")

st.header("3. Preguntas de negocio")

st.write("""
A partir de la estructura de datos presentada, el análisis se orienta a responder una serie de preguntas relevantes desde la perspectiva de riesgo y negocio:

- ¿Qué productos concentran la mayor parte del capital colocado y cuáles ofrecen las tasas más altas?
- ¿En qué segmentos del portafolio se observan mayores niveles de mora?
- ¿Qué explica mejor el deterioro crediticio: el ingreso del cliente o su score de riesgo?
- ¿Existen patrones transaccionales que funcionen como señales tempranas de alerta?
- ¿Qué clientes representan una oportunidad comercial atractiva por su bajo riesgo y alto potencial de vinculación?

Para responder estas preguntas, la página se organiza en cinco etapas: 

1. Radiografía inicial de la cartera
2. Análisis de mora por producto
3. Comparación entre ingreso y score como predictores de riesgo
4. Exploración de señales tempranas a partir del comportamiento transaccional 
5. Finalmente, la identificación de un segmento objetivo de alto valor comercial.
""")

st.header("Fase 1. Radiografía de la cartera")





st.markdown("---")

st.subheader("Modelo relacional del dataset")



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

# ============================================================
# 2.4 Actividad financiera, tipo de cuenta y riesgo
# ============================================================

st.markdown("### 2.4 ¿La actividad financiera del cliente está asociada al riesgo de mora?")
st.markdown("""
**🎯 Pregunta**  
¿Los clientes con mayor actividad transaccional o con múltiples tipos de cuenta presentan menor probabilidad de atraso en sus pagos?
""")

st.markdown("#### Consulta SQL")

q_actividad_riesgo = """
WITH info_tran_usuario AS (
  SELECT 
    t.customer_id,
    COUNT(*) AS numero_transacciones,
    AVG(t.amount) AS promedio_monto
  FROM transactions t
  GROUP BY t.customer_id
),
tipo_cuenta AS (
  SELECT
    a.customer_id,
    CASE
      WHEN SUM(a.account_type = 'Savings') > 0 AND SUM(a.account_type = 'Checking') > 0 THEN 'Both'
      WHEN SUM(a.account_type = 'Savings') > 0 THEN 'Savings'
      WHEN SUM(a.account_type = 'Checking') > 0 THEN 'Checking'
      ELSE 'Unknown'
    END AS account_type
  FROM accounts a
  GROUP BY a.customer_id
)
SELECT 
  tc.account_type,
  AVG(it.numero_transacciones) AS promedio_transacciones,
  AVG(it.promedio_monto) AS promedio_monto,
  AVG(CASE WHEN p.days_late > 0 THEN 1 ELSE 0 END) AS proporcion_riesgo
FROM payments p
JOIN info_tran_usuario it ON p.customer_id = it.customer_id
JOIN tipo_cuenta tc       ON p.customer_id = tc.customer_id
GROUP BY tc.account_type
ORDER BY tc.account_type;
"""

st.code(q_actividad_riesgo, language="sql")

# ------------------------------------------------
# Ejecutar consulta
# ------------------------------------------------
con = duckdb.connect(DB_PATH)
df_actividad_riesgo = con.execute(q_actividad_riesgo).df()
con.close()

# ------------------------------------------------
# Resultados contraídos
# ------------------------------------------------
with st.expander("Ver resultados"):

    st.markdown("#### Tabla de resultados")
    st.dataframe(df_actividad_riesgo, use_container_width=True)

    # ------------------------------------------------
    # Gráfica 1: proporción de riesgo por tipo de cuenta
    # ------------------------------------------------
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick
    import numpy as np

    tipos = df_actividad_riesgo["account_type"]
    riesgo = df_actividad_riesgo["proporcion_riesgo"]
    transacciones = df_actividad_riesgo["promedio_transacciones"]

    fig_actividad_riesgo, ax = plt.subplots(figsize=(8, 5), dpi=130)

    ax.bar(tipos, riesgo)
    ax.set_title("Proporción de mora por tipo de cuenta", pad=12)
    ax.set_xlabel("Tipo de cuenta")
    ax.set_ylabel("Proporción de mora")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.grid(True, axis="y", alpha=0.25)

    plt.tight_layout()

    st.markdown("#### Visualización")
    st.pyplot(fig_actividad_riesgo, use_container_width=True)

    st.markdown("""
**Interpretación inicial**

- Los clientes con **cuentas Checking** presentan la menor proporción de atraso, con un valor cercano al **12.3%**.  
- Los clientes con **cuentas Savings** muestran una mora observada ligeramente mayor, alrededor de **13.8%**.  
- Los clientes con **ambos tipos de cuenta (Both)** registran la mayor proporción de mora, aproximadamente **14.4%**.  

En cuanto a la actividad financiera, el promedio de transacciones es bastante similar entre grupos, con valores cercanos a **10 transacciones por cliente**.  
Esto sugiere que, en este dataset sintético, **no se observa una relación fuerte entre una mayor actividad transaccional y una menor probabilidad de atraso**.

En conjunto, los resultados muestran que las diferencias en riesgo por tipo de cuenta existen, pero son moderadas, y no parecen explicarse únicamente por el volumen promedio de transacciones.
""")

st.markdown("---")
st.header("3. Explicación de las tablas de la base de datos")
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







