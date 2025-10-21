import streamlit as st

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Calculateur Nutrition Endurance", page_icon="🏃‍♂️", layout="centered")

st.title("🏃‍♂️ Calculateur de glucides – version avancée (15 → 150 g/h)")
st.markdown(
    """
    Estimation personnalisée de ton besoin en **glucides (g/h)** selon les dernières recommandations scientifiques.  
    Plage étendue : **15 → 150 g/h**, adaptée aux efforts jusqu’à **40 heures**.
    """
)

# ---- Utils ----
def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def heures_entiere_et_minutes(h, m):
    """Convertit heures + minutes en heures décimales"""
    return h + (m / 60)

# ---- Inputs ----
st.header("📋 Données athlète et course")

col1, col2 = st.columns(2)
with col1:
    poids = st.slider("Poids (kg)", 40, 120, 70, 1)
    intensite = st.slider("Intensité perçue (RPE/10)", 1, 10, 7)
with col2:
    temperature = st.slider("Température (°C)", 0, 40, 20)
    sudation = st.slider("Transpiration (0=faible, 10=forte)", 0, 10, 5)

st.subheader("⏱ Durée de l'effort")
c1, c2 = st.columns(2)
with c1:
    heures = st.number_input("Heures", min_value=0, max_value=40, value=2)
with c2:
    minutes = st.selectbox("Minutes", options=[0,15,30,45], index=0)
duree = heures_entiere_et_minutes(heures, minutes)

# ---- Tolérance digestive ----
st.subheader("😌 Tolérance digestive")
digestif = st.slider("Tolérance digestive (0 = très sensible, 10 = aucune gêne)", 0, 10, 8)
inconfort = st.slider("Historique d’inconfort digestif (0 = jamais, 10 = fréquent)", 0, 10, 2)

# ---- Calculs ----
# pondérations ajustables
w_duree, w_intensite, w_poids, w_temp, w_dig, w_sud, w_inconf = 0.30, 0.25, 0.15, 0.10, 0.10, 0.05, 0.05

# normalisations 0–1
S_duree = clamp(duree / 8, 0, 1)  # jusqu’à 8h influence max, puis saturé
S_intensite = clamp(intensite / 10, 0, 1)
S_poids = clamp((poids - 40) / 80, 0, 1)
S_temp = clamp((temperature - 5) / 35, 0, 1)
S_sud = sudation / 10
S_dig = digestif / 10
S_inconf = 1 - (inconfort / 10)

# Score brut
S = (
    w_duree * S_duree +
    w_intensite * S_intensite +
    w_poids * S_poids +
    w_temp * S_temp +
    w_dig * S_dig +
    w_sud * S_sud +
    w_inconf * S_inconf
)
S = clamp(S, 0, 1)

# ---- Effet digestif (plus fort) ----
# Modulateur exponentiel : tolérance faible = forte réduction
facteur_digestif = 0.75 + 0.25 * (S_dig**1.5)   # 0.75–1 selon tolérance
S *= facteur_digestif
S = clamp(S, 0, 1)

# ---- Mapping 15–150 g/h ----
LOW, HIGH = 15, 150
mid = LOW + (HIGH - LOW) * S
band = 15
g_min = clamp(mid - band, LOW, HIGH)
g_max = clamp(mid + band, LOW, HIGH)

# ---- Résultats ----
st.header("📊 Résultats")
st.metric("Durée totale", f"{heures}h {minutes:02d}min")
st.metric("Score global", f"{S*100:.0f}/100")
st.progress(S)

st.subheader("🎯 Recommandation glucides (g/h)")
st.write(f"**Min : {g_min:.0f} g/h** | **Cible : {mid:.0f} g/h** | **Max : {g_max:.0f} g/h**")

st.markdown("---")
st.markdown(
    """
    **Interprétation :**  
    - 15–40 g/h → très court, faible intensité ou faible tolérance  
    - 60–90 g/h → zone optimale pour la majorité des marathoniens  
    - 100–150 g/h → ultra-endurance, athlètes bien entraînés à l’ingestion de glucides  
    """
)

st.caption(
    "Modèle basé sur les travaux de Burke (2021), Jeukendrup (2014), Stellingwerff (2019). "
    "L'effet digestif est amplifié pour refléter les limitations d'absorption intestinales (max ~90–120 g/h glucose+fructose)."
)
