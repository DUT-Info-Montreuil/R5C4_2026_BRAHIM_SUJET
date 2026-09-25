import streamlit as st

st.set_page_config(
    page_title="Tableau de bord - Parties", page_icon="🎮", layout="wide"
)

st.title("🎮 Tableau de bord de gestion des parties")
st.sidebar.success("Sélectionnez une page ci-dessus.")

st.markdown("""
### Bienvenue sur l'application Streamlit !

Naviguez via le menu latéral pour :
- **Consulter les parties** (Filtres, tri, pagination)
- **Visualiser les indicateurs clés** (KPIs & comparaison avec l'année précédente)
""")