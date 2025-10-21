import streamlit as st

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Calculateur Nutrition Endurance", page_icon="🏃‍♂️", layout="centered")

st.title("🏃‍♂️ Calculateur de glucides – modèle scientifique (15 → 150 g/h)")
st.markdown(
    """
    Cet outil estime ta **recommandation personnalisée de glucides (g/h)** selon la durée, 
    l’intensité, le poids, la chaleur et ta **tolérance digestive**.  
    Basé sur les recommandations de la littérature : **15 → 150 g/h**.
    """
)

# --- Petite fonction utilitaire ---
def clamp(x, lo, hi):
    return max(lo, min(hi, x))

# ------------------ QUESTIONNAIRE ------------------
st.header("📋 Questionnaire rapide")

# Poids
poids = st.slider("Poids de l'athlète (kg)", 40, 120, 70)

# Durée d’effort
duree = st.slider("Durée prévue de l’effort (heures)", 0.5, 12.0, 2.0, 0.25)

# Intensité perçue
intensite = st.slider("Intensité (RPE / 10)", 1, 10, 7)

# Température
temperature = st.slider("Température ambiante (°C)", 5, 40, 20)

# Tolérance digestive
st.subheader("😌 Tolérance digestive")
digestif = st.slider(
    "Comment évalues-tu ta tolérance digestive en course ? (0 = très sensible, 10 = aucun souci)",
    0, 10, 7
)

# Hydratation / sudation
st.subheader("💧 Transpiration et chaleur")
sudation = st.slider(
    "Degré de sudation (0 = très faible, 10 = je transpire beaucoup)",
    0, 10, 5
)

# Historique d’inconfort
st.subheader("🤕 Inconfort digestif passé")
inconfort = st.slider(
    "As-tu déjà eu des problèmes digestifs importants en compétition ? (0 = jamais, 10 = souvent)",
    0, 10, 2
)

# ------------------ CALCUL DU SCORE ------------------
# pondérations ajustables
w_duree, w_intensite, w_poids, w_temp, w_dig, w_sud, w_inconf = 0.25, 0.25, 0.15, 0.10, 0.10, 0.10, 0.05

# normalisations sur 0–1
S_duree = clamp(duree / 6, 0, 1)           # 6h = effort long
S_intensite = clamp(intensite / 10, 0, 1)
S_poids = clamp((poids - 40) / 80, 0, 1)   # 40–120 kg → 0–1
S_temp = clamp((temperature - 5) / 35, 0, 1)
S_dig = digestif / 10
S_sud = sudation / 10
S_inconf = 1 - (inconfort / 10)

# score global pondéré
S = (
    w_duree * S_duree
    + w_intensite * S_intensite
    + w_poids * S_poids
    + w_temp * S_temp
    + w_dig * S_dig
    + w_sud * S_sud
    + w_inconf * S_inconf
)
S = clamp(S, 0, 1)

# ------------------ CONVERSION EN g/h ------------------
LOW, HIGH = 15, 150
mid = LOW + (HIGH - LOW) * S
band = 15  # +/- 15 g/h d'incertitude
g_min = clamp(mid - band, LOW, HIGH)
g_max = clamp(mid + band, LOW, HIGH)

# ------------------ AFFICHAGE ------------------
st.header("📊 Résultats personnalisés")
st.metric("Score global", f"{S*100:.0f} / 100")
st.progress(S)
st.subheader("🎯 Recommandation en glucides (g/h)")
st.write(f"**Min :** {g_min:.0f} g/h | **Cible :** {mid:.0f} g/h | **Max :** {g_max:.0f} g/h")

st.markdown("---")
st.markdown(
    """
    **Interprétation** :
    - 🔵 *< 40 g/h* → effort court, basse intensité, petit gabarit ou tolérance fragile  
    - 🟢 *60–90 g/h* → zone optimale pour la majorité des coureurs  
    - 🔴 *> 100 g/h* → intensité ou durée élevées, athlète entraîné à l’ingestion de glucides  
    - La plage **15–150 g/h** couvre les cas extrêmes (marathon à ultra).  
    """
)

st.caption(
    "Sources : Burke et al., 2021 – Jeukendrup 2014 – Asker Jeukendrup (‘Fueling the Athlete’). "
    "Modèle heuristique, à ajuster selon tests terrain."
)
