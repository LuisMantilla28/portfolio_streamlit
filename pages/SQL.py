import streamlit as st



st.title("SQL Projects")
st.subheader("Data analysis, querying and database modeling")

st.markdown("---")

st.write(
    """
This section showcases projects developed using SQL for data extraction,
transformation, analysis and business insight generation.

The focus is on:
- Writing optimized queries
- Working with large relational datasets
- Designing analytical views
- Extracting meaningful KPIs
"""
)

st.markdown("---")

st.markdown("## 🔎 What you will find here")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Analytical Queries")
    st.write(
        """
        - Aggregations and grouping
        - Window functions
        - Subqueries
        - Joins (INNER, LEFT, RIGHT)
        """
    )

with col2:
    st.markdown("### 🗂 Database Modeling")
    st.write(
        """
        - Relational schema design
        - Primary & foreign keys
        - Index considerations
        - Performance awareness
        """
    )

st.markdown("---")

st.markdown("## 🚀 Featured Projects (Coming Soon)")

st.info("Projects and dashboards will be added here.")
