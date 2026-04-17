import streamlit as st
import navigation
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import streamlit as st
import seaborn as sns

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

st.subheader("Fase 1. Radiografía de la cartera")

st.write("""
El primer paso del análisis consiste en entender la composición general de la cartera. Antes de estudiar incumplimiento o señales de alerta, es necesario identificar en qué productos se concentra el capital colocado, qué tan diversificada es la exposición y cuáles son las condiciones promedio de colocación.

Desde la perspectiva de negocio, esta radiografía permite responder una pregunta fundamental: **dónde está realmente expuesto el banco**. Un producto puede tener una tasa alta y parecer atractivo, pero si su participación dentro de la cartera es baja, su impacto estratégico es limitado. De forma análoga, un producto con tasas moderadas puede representar un riesgo sistémico mayor si concentra la mayor parte del capital.

En esta fase consolidamos la información de la tabla loans por tipo de producto, lo que nos permite identificar la exposición de capital del banco (capital_colocado), el volumen de operaciones (total_creditos) y el rendimiento esperado pactado a través de la tasa promedio efectivo anual."
""")

query_radiografia = """
SELECT 
    product,
    COUNT(loan_id) AS total_creditos,
    SUM(amount) AS capital_colocado,
    ROUND(AVG(interest_rate) * 100, 2) AS tasa_promedio_ea
FROM loans
GROUP BY product
ORDER BY capital_colocado DESC;
"""

st.markdown("### Consulta SQL")
st.code(query_radiografia, language="sql")

con = duckdb.connect(DB_PATH, read_only=True)
df_radiografia = con.execute(query_radiografia).df()
con.close()
st.dataframe(df_radiografia, use_container_width=True, hide_index=True)


st.write("""

Al observar los resultados, se identifican tres hallazgos críticos sobre la estructura financiera del banco:
1. Concentración de Capital en Activos Garantizados: El producto "Vehículo" es el motor de colocación del banco. Aunque solo representa el 20% de la cantidad de créditos, concentra más de 3 millones de dolares, lo que equivale a casi el 48% del capital total de la muestra. Esto indica un modelo de negocio fuertemente respaldado por garantías reales.
2. Liderazgo en Margen vs. Baja Exposición: Las "Tarjetas de Crédito" presentan la tasa más alta del portafolio (33.16%), superando por más de 12 puntos básicos a la Libranza. Sin embargo, es el producto con menor capital colocado (460k), sugiriendo que es un producto de alta rentabilidad pero con cupos más controlados o menor penetración.
3. Dominio de Consumo en el Mercado Masivo: El producto "Consumo" es el más popular en volumen (348 créditos). Su tasa del 26.79% lo posiciona como un producto equilibrado: masivo y con un rendimiento superior al promedio de la cartera comercial.


Decisiones Estratégicas (Preliminares)
A partir de esta radiografía, la dirección del banco podría considerar las siguientes acciones:

- Protección del Activo Crítico: Dado que casi la mitad del dinero está en "Vehículo", cualquier fluctuación en este mercado impactaría fuertemente la solvencia del banco. Se deben mantener políticas de avalúo estrictas.
- Oportunidad de Expansión en Tarjetas: Existe un margen de rentabilidad muy atractivo en tarjetas. Si la mora lo permite, hay espacio para aumentar el capital colocado en este producto y maximizar los ingresos por intereses.
- Fidelización en Libranza: Siendo el producto con la tasa más baja (20.94%), la Libranza debe ser utilizada como "producto ancla" para atraer clientes de bajo riesgo que luego puedan migrar a Consumo o Tarjeta.

Este análisis inicial nos muestra una cartera teóricamente rentable, especialmente en el segmento de tarjetas. Sin embargo, la tasa de interés no es utilidad real hasta que el cliente paga.
El siguiente paso lógico es validar si ese margen del 33% en tarjetas se mantiene o si se ve erosionado por el incumplimiento. Por lo tanto, nuestra próxima consulta se enfocará en el Análisis de Mora y Comportamiento de Pago, para determinar si los productos con mayores tasas son también los que presentan mayores retrasos.
""")


st.subheader("Fase 2. El Impacto de la Mora en la Rentabilidad")
st.write("""
Una tasa de interés alta es atractiva solo si el cliente paga a tiempo. En esta etapa, cruzamos la tabla de préstamos con la de pagos para validar si el margen superior que vimos en las Tarjetas de Crédito se ve amenazado por el incumplimiento. Utilizamos una CTE (Common Table Expression) para categorizar cada una de las más de 13,000 cuotas y calcular dos métricas críticas: el promedio de días de retraso y el índice de mora, que representa el porcentaje de cuotas que no se pagaron en la fecha pactada.
""")

query_mora = """
WITH DetalleMora AS (
    SELECT 
        l.product,
        p.days_late,
        CASE WHEN p.days_late > 0 THEN 1 ELSE 0 END AS es_pago_tardio
    FROM loans l
    JOIN payments p ON l.loan_id = p.loan_id
)
SELECT 
    product,
    ROUND(AVG(days_late), 2) AS promedio_dias_retraso,
    SUM(es_pago_tardio) * 100.0 / COUNT(*) AS indice_mora_cuotas
FROM DetalleMora
GROUP BY 1
ORDER BY promedio_dias_retraso DESC;
"""

st.markdown("### Consulta SQL")
st.code(query_mora, language="sql")

con = duckdb.connect(DB_PATH, read_only=True)
df_mora = con.execute(query_mora).df()
con.close()
st.dataframe(df_mora, use_container_width=True, hide_index=True)

st.write("""
Al analizar los resultados, observamos un patrón de riesgo consistente pero con matices importantes:

1. Confirmación del Perfil de Riesgo en Tarjetas: Como se sospechaba, la Tarjeta de Crédito lidera tanto el promedio de retraso (2.76 días) como el índice de mora (13.76%). Esto justifica que sea el producto con la tasa más alta; el banco cobra más porque, efectivamente, es donde los clientes fallan más.
2. Estabilidad de la Libranza: El producto Libranza presenta el mejor comportamiento de pago (mora del 12.95% y solo 2.52 días de retraso). Esto es coherente con la naturaleza del producto, donde las cuotas suelen descontarse directamente de la nómina del cliente, reduciendo la probabilidad de olvido o desvío de fondos.
3. Homogeneidad en la Mora: Un hallazgo sorprendente es la poca dispersión entre productos. La diferencia entre el producto más riesgoso (Tarjeta) y el más seguro (Libranza) es de apenas 0.81 puntos porcentuales en el índice de mora. Esto sugiere que el riesgo de impago en NovaBank está más influenciado por el perfil del cliente que por el tipo de préstamo en sí.

Decisiones Estratégicas Basadas en la Mora

- Optimización de Cobranzas en Tarjetas: Dado que el 13.7% de las cuotas de tarjetas entran en mora, se recomienda implementar recordatorios preventivos (SMS/Email) 3 días antes del vencimiento para este producto específico.
- Margen de Maniobra en Vehículos: A pesar de tener cuotas mucho más altas en dinero (como vimos en la Fase 1), los clientes de Vehículo son casi tan cumplidos como los de Consumo (13.49% de mora). El banco puede estar tranquilo con su exposición en este sector, ya que la garantía real parece incentivar el pago oportuno.

Hemos confirmado que las tarjetas son el producto más riesgoso, pero la diferencia con los demás productos es pequeña. Esto nos plantea una nueva e inquietante pregunta:

Si la mora es similar en todos los productos, ¿quiénes son realmente los clientes que no pagan? ¿Son las personas con ingresos bajos las que tienen más dificultades, o existe una paradoja de riesgo donde clientes con altos ingresos también presentan moras altas debido a su score crediticio?
""")



st.subheader("Fase 3. El Mito del Ingreso vs. La Realidad del Score")
st.write("""
En el sector financiero, existe la creencia común de que a mayores ingresos, menor es el riesgo de impago. Sin embargo, para un analista de datos, las suposiciones deben validarse con evidencia. En esta fase, cruzamos la información demográfica de los clientes con su historial real de pagos. categorizamos a los clientes en tres niveles de riesgo (Bajo, Medio y Alto) basándonos en su risk_score y comparamos su ingreso promedio frente a su mora histórica (promedio de días de retraso).
""")

query_ingreso = """
WITH AnalisisPerfil AS (
    SELECT 
        c.customer_id,
        c.segment,
        c.risk_score,
        c.income_monthly,
        AVG(p.days_late) AS mora_media_cliente
    FROM customers c
    JOIN payments p ON c.customer_id = p.customer_id
    GROUP BY 1, 2, 3, 4
)
SELECT 
    segment,
    CASE 
        WHEN risk_score < 500 THEN 'Riesgo Alto'
        WHEN risk_score < 700 THEN 'Riesgo Medio'
        ELSE 'Riesgo Bajo'
    END AS categoria_riesgo,
    ROUND(AVG(income_monthly), 0) AS ingreso_promedio,
    ROUND(AVG(mora_media_cliente), 2) AS mora_historica
FROM AnalisisPerfil
GROUP BY 1, 2
ORDER BY 1, 4 DESC;
"""

st.markdown("### Consulta SQL")
st.code(query_ingreso , language="sql")

con = duckdb.connect(DB_PATH, read_only=True)
df_ingreso  = con.execute(query_ingreso ).df()
con.close()
st.dataframe(df_ingreso , use_container_width=True, hide_index=True)


# Configuración de estilo profesional
sns.set_theme(style="whitegrid")
plt.figure(figsize=(12, 7))

# Aseguramos el orden lógico del riesgo para que la historia fluya
orden_riesgo = ['Riesgo Bajo', 'Riesgo Medio', 'Riesgo Alto']

# Creamos el gráfico de barras
ax = sns.barplot(
    data=df_ingreso, 
    x='categoria_riesgo', 
    y='mora_historica', 
    hue='segment',
    order=orden_riesgo,
    palette='viridis' # Colores profesionales y legibles
)

# Añadimos etiquetas de datos sobre las barras para mayor claridad
for container in ax.containers:
    ax.bar_label(container, fmt='%.2f', padding=3, fontsize=10, fontweight='bold')

# Títulos y etiquetas con estilo corporativo
plt.title('La Paradoja del Riesgo: Días de Mora por Segmento y Score', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Categoría de Riesgo (Basada en Score)', fontsize=12, labelpad=10)
plt.ylabel('Promedio Días de Mora', fontsize=12, labelpad=10)
plt.legend(title='Segmento de Cliente', title_fontsize='11', loc='upper left')

# Limpiamos el diseño eliminando bordes innecesarios
sns.despine(left=True, bottom=True)

plt.tight_layout()
st.pyplot(plt)

st.write("""
Al observar la tabla completa, emergen tres descubrimientos que redefinirán la estrategia del banco:

1. El "Gran Ecualizador": El Score de Riesgo:
    - Cuando un cliente tiene Riesgo Bajo (Score > 700), el nivel de ingresos es irrelevante para su puntualidad. Los tres segmentos (SME, Mass y Affluent) se comportan de forma impecable, con moras mínimas entre 0.87 y 1.03 días. La disciplina financiera es universal y no depende del tamaño de la cuenta bancaria.
2. La Alerta Roja: SME y Mass en Riesgo Alto:
    - Existe un empate técnico en la peor mora del banco: los clientes de Riesgo Alto en el segmento SME (4.13 días) y Mass (4.12 días).
    - Lo preocupante: Una SME gana en promedio 1,989, casi 5 veces más que un cliente masivo (439), y aun así tiene la misma mora. Esto indica que el flujo de caja de un pequeño negocio puede ser tan inestable como el de una persona de bajos recursos si no hay una gestión de riesgo sólida.
3. El Efecto "Colchón" del Segmento Affluent:
    - En los grupos de Riesgo Alto, el segmento Affluent (2.08 días) tiene la mitad de mora que el segmento Mass (4.12 días). Aquí se demuestra que, ante un mal hábito crediticio, el alto ingreso (2,361 vs 439) ayuda a "tapar" el problema o resolverlo más rápido, pero no lo elimina.

Decisiones Estratégicas (Basadas en Hallazgos)

- Revisión de Política para SME: Los datos muestran que las SME con score bajo son de altísimo peligro. Se recomienda endurecer los requisitos de garantías para negocios con scores menores a 500, ya que su capacidad de pago es tan errática como la del mercado masivo.
- Fidelización del "Cliente Diamante": Los clientes de Riesgo Bajo en todos los segmentos (moras < 1 día) son los activos más valiosos. Se propone crear un programa de beneficios o tasas preferenciales para asegurar que no migren a la competencia.
- Segmentación de Cobranza: El equipo de cobranza debe priorizar al grupo SME/Mass de Riesgo Alto, ya que son los que más tardan en regularizar su situación (más de 4 días de retraso promedio).

Hemos confirmado que el Score de Riesgo es el predictor de comportamiento más potente, pero también hemos visto que incluso en segmentos de altos ingresos hay personas que fallan.

Esto nos lleva a una pregunta de detección temprana: Antes de que un cliente de Riesgo Alto llegue a esos 4 días de mora, ¿existen señales en su comportamiento diario?
""")


st.subheader("Fase 4. Señales de Alerta Temprana")
st.write("""
Hasta ahora, hemos analizado el riesgo como una foto estática basada en el score y el ingreso. Sin embargo, un banco moderno debe ser capaz de detectar el riesgo en movimiento. En esta fase, analizamos el comportamiento transaccional diario de los clientes, comparando a aquellos que ya presentan una mora crítica (>7 días) frente a los que están al día. El objetivo es identificar patrones de abandono de canales o señales de falta de liquidez que sirvan como alertas tempranas.
""")

query_alerta = """
WITH PerfilPuntualidad AS (
    SELECT 
        customer_id,
        CASE WHEN AVG(days_late) > 7 THEN 'Moroso' ELSE 'Puntual' END AS estado_cliente
    FROM payments
    GROUP BY customer_id
)
SELECT 
    pp.estado_cliente,
    t.tx_type,
    COUNT(t.tx_id) AS volumen_transacciones,
    ROUND(AVG(t.amount), 2) AS monto_promedio_tx
FROM transactions t
JOIN PerfilPuntualidad pp ON t.customer_id = pp.customer_id
GROUP BY 1, 2
ORDER BY 1, 3 DESC;
"""

st.markdown("### Consulta SQL")
st.code(query_alerta , language="sql")

con = duckdb.connect(DB_PATH, read_only=True)
df_alerta  = con.execute(query_alerta ).df()
con.close()
st.dataframe(df_alerta , use_container_width=True, hide_index=True)


# Configuración de estilo
sns.set_theme(style="white")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# --- Gráfico 1: Volumen de Transacciones ---
# Usamos escala logarítmica para que las barras de los morosos sean visibles 
# y se note la diferencia de magnitud.
sns.barplot(
    data=df_alerta, 
    x='tx_type', 
    y='volumen_transacciones', 
    hue='estado_cliente', 
    ax=ax1,
    palette='magma'
)
ax1.set_yscale("log") # Escala logarítmica para ver la diferencia de miles vs decenas
ax1.set_title('Frecuencia de Uso por Canal (Escala Log)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Tipo de Transacción')
ax1.set_ylabel('Número de Transacciones (Log)')

# --- Gráfico 2: Monto Promedio por Transacción ---
sns.barplot(
    data=df_alerta, 
    x='tx_type', 
    y='monto_promedio_tx', 
    hue='estado_cliente', 
    ax=ax2,
    palette='magma'
)
ax2.set_title('Ticket Promedio: Puntuales vs Morosos', fontsize=14, fontweight='bold')
ax2.set_xlabel('Tipo de Transacción')
ax2.set_ylabel('Monto Promedio ($)')

# Añadir etiquetas de datos en el gráfico de montos
for container in ax2.containers:
    ax2.bar_label(container, fmt='%.0f', padding=3, fontsize=9)

plt.suptitle('Análisis del "Desierto Transaccional" en Clientes con Mora', fontsize=18, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()
st.pyplot(plt)

st.write("""
Al comparar ambos grupos, los datos revelan una diferencia drástica y reveladora en el estilo de vida financiero:
1. El "Abandono del Ecosistema Digital":
    - Los clientes Puntuales utilizan todo el abanico de servicios, destacando montos altos en BillPay (826.00) y Transfer (747.03).
    - Por el contrario, en el grupo Moroso, el uso de BillPay es inexistente (0) y las transferencias son mínimas. Esto sugiere que cuando un cliente empieza a fallar en sus créditos, lo primero que hace es dejar de usar el banco para pagar sus servicios básicos, rompiendo el vínculo digital con la entidad.
2. Diferencia Crítica en la Capacidad de Gasto:
    - Existe una brecha enorme en los montos. Mientras un cliente puntual gasta en promedio 201.93 en una compra POS (comercio), el cliente moroso solo gasta 78.67.
    - Esto indica que el cliente moroso no solo está fallando en su crédito, sino que su capacidad de consumo diario se ha reducido a menos de la tercera parte, una señal clara de estrés financiero profundo.
3. La "Fuga" hacia el Efectivo:
    - Aunque el volumen es bajo, el grupo moroso mantiene actividad en ATM (Cajeros) y POS. Esto demuestra que el poco flujo de caja que poseen lo destinan a gastos de supervivencia inmediata (efectivo y compras físicas pequeñas), alejándose de los canales de ahorro o pagos programados.

Decisiones Estratégicas (Alertas Tempranas)

- Indicador de Alerta "BillPay Zero": Se propone crear un evento automático: si un cliente que solía pagar sus facturas (BillPay) deja de hacerlo por 30 días, el sistema debe etiquetarlo como "Riesgo Emergente", incluso antes de que falle en su primera cuota de préstamo.
- Reducción Proactiva de Riesgo: Para clientes que muestren una caída drástica en su ticket promedio de POS (de >200 a <80), el banco debería bloquear preventivamente los aumentos de cupo en tarjetas de crédito.
- Campaña de Retención Digital: Ofrecer incentivos para el uso de canales digitales a clientes en riesgo para mantener la visibilidad de su flujo de caja y evitar que se vuelvan "invisibles" al operar solo en efectivo.

Hemos completado el ciclo: sabemos qué productos son rentables, quiénes tienen peor score, y cómo se comportan transaccionalmente cuando están en problemas.

La pregunta final para cerrar esta estrategia de negocio es: ¿Cómo crecemos ahora de forma segura?

En el paso final de este informe, identificaremos al 'Golden Target': clientes que hoy son sumamente activos en transacciones, tienen ingresos sólidos y un riesgo bajo, pero que extrañamente no poseen ningún préstamo con nosotros. Ellos son la clave para sanear la cartera y maximizar la rentabilidad sin aumentar el riesgo.
""")

st.subheader("Fase 5. Conclusión y Estrategia: El Segmento 'Golden Target' ")
st.write("""
Tras identificar los focos de riesgo y los patrones de comportamiento de los clientes morosos, la última etapa de este análisis se enfoca en la expansión rentable. El objetivo es detectar a los clientes 'invisibles' para el área de crédito: personas que utilizan activamente el banco, pero que aún no poseen préstamos. Mediante el uso de CTEs y JOINS de exclusión, filtramos a los clientes con scores superiores a 600 y actividad transaccional constante para proponer una estrategia de colocación de bajo riesgo.

Al intentar buscar clientes con scores perfectos (>750) y sin deudas, descubrimos que NovaBank tiene una penetración de mercado tan alta que casi todos nuestros clientes premium ya tienen un crédito con nosotros. Esto es una excelente noticia para el equipo de ventas, pero un reto para el crecimiento.

Por ello, decidimos ajustar nuestra búsqueda hacia el 'Top de Oportunidad': clientes con scores superiores a 600 y actividad constante. Estos no son 'diamantes puros', pero son clientes sólidos que están usando el banco para sus gastos diarios y que representan nuestra mejor oportunidad de expansión inmediata sin comprometer la salud de la cartera.
""")

query_golden = """
WITH ClientesPremium AS (
    SELECT 
        cust.customer_id, 
        cust.income_monthly, 
        cust.risk_score
    FROM customers AS cust
    LEFT JOIN loans AS lon ON cust.customer_id = lon.customer_id
    WHERE lon.loan_id IS NULL -- Que no tengan préstamos
    AND cust.risk_score > 600 -- un escore para considerar como bueno
),
ActividadTransaccional AS (
    SELECT 
        customer_id, 
        COUNT(*) AS frecuencia_uso
    FROM transactions
    GROUP BY customer_id
    HAVING COUNT(*) >= 5 -- ver los mas activos del grupo 
)
SELECT 
    cp.customer_id,
    cp.income_monthly,
    cp.risk_score,
    act.frecuencia_uso
FROM ClientesPremium AS cp
JOIN ActividadTransaccional AS act ON cp.customer_id = act.customer_id
ORDER BY cp.risk_score DESC, cp.income_monthly DESC
LIMIT 10;
"""

st.markdown("### Consulta SQL")
st.code(query_golden , language="sql")

con = duckdb.connect(DB_PATH, read_only=True)
df_golden = con.execute(query_golden ).df()
con.close()
st.dataframe(df_golden , use_container_width=True, hide_index=True)



st.write("""
Al analizar el listado de los 10 candidatos principales, emergen perfiles de alto valor que el banco debería capitalizar de inmediato:

1. El Cliente de Alta Fidelidad (Caso ID 3): Identificamos a un cliente con un ingreso sobresaliente de 6,869 y la mayor frecuencia transaccional de la muestra (17 operaciones). Con un score de 697, es el candidato ideal para un producto premium (como una Tarjeta Black o un crédito de Consumo de alto monto), ya que su operatividad diaria demuestra una dependencia total del ecosistema del banco.
2. Solidez en el Score (Caso ID 431 y 8): Los clientes en las primeras posiciones presentan scores de 734 y 732. Son perfiles con un hábito de pago excelente que hoy no generan intereses para el banco. Su inclusión en la cartera de créditos ayudaría a equilibrar el promedio de mora que vimos en las fases anteriores.
3. Potencial de Inclusión (Caso ID 86): Incluso con ingresos más moderados (881), existen clientes con scores sólidos (696) que están usando el banco de forma recurrente. Esto demuestra que la oportunidad de crecimiento no es exclusiva de los segmentos altos, sino de cualquiera con disciplina financiera.


Decisiones Finales y Recomendaciones Estratégicas

Con base en todo el análisis realizado (desde la rentabilidad por producto hasta la detección de este Golden Target), se proponen las siguientes acciones:

- Oferta de 'Bajo Roce': Iniciar una campaña de pre-aprobados para estos 10 IDs. Al ser clientes activos y de bajo riesgo, el proceso de aprobación debe ser automático para garantizar una tasa de conversión alta.
- Balanceo de Cartera: Por cada nuevo crédito otorgado a este segmento, el banco reduce su riesgo relativo, permitiéndonos compensar las pérdidas potenciales del segmento Mass / Riesgo Alto identificado en la Fase 3.
- Monitoreo Transaccional: Establecer la Frecuencia de Uso (como vimos en el ID 3 con sus 17 tx) como un nuevo criterio de aprobación. Un cliente que usa mucho el banco tiene un "costo de quedar mal" más alto, lo que lo hace intrínsecamente más responsable.

A través de este viaje por los datos, hemos transformado simples tablas en una hoja de ruta estratégica:

1. Identificamos que el Vehículo protege nuestro capital y la Tarjeta nuestro margen.
2. Desmitificamos el ingreso, demostrando que el Score es el verdadero predictor de la mora.
3. Descubrimos que la caída en el uso de BillPay y el ticket de POS son señales de alerta antes de que ocurra el impago.
4. Y finalmente, encontramos el 'Tesoro Escondido': clientes fieles y solventes listos para ser contactados.

El banco está ahora posicionado para dejar de reaccionar ante el riesgo y empezar a predecirlo y gestionarlo.
""")








