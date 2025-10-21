import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ---------- CONFIG ----------
st.set_page_config(page_title="Calculateur Nutrition Endurance", page_icon="🏃‍♂️", layout="centered")

st.title("🏃‍♂️ Calculateur de glucides – version visuelle et complète (15 → 150 g/h)")
st.markdown(
    """
    Cet outil estime ton besoin en **glucides (g/h)** selon la littérature scientifique, 
    avec un rendu visuel et une recommandation de ratio **glucose : fructose = 1 : 1**.
    """
)

# ---------- UTILS ----------
def clamp(x, lo, hi): return max(lo, min(hi, x))
def heures_entiere_et_minutes(h, m): return h + (m / 60)

# ---------- ENTRÉES ----------
st.header("📋 Données athlète et course")

col1, col2 = st.columns(2)
with col1:
    poids = st.slider("Poids (kg)", 40, 120, 70, 1)
    rpe = st.slider("Intensité perçue (RPE / 10)", 1, 10, 7)
with col2:
    temperature = st.slider("Température (°C)", 0, 40, 20)
    sudation = st.slider("Transpiration (0=faible, 10=forte)", 0, 10, 5)

st.subheader("⏱ Durée de l'effort")
c1, c2 = st.columns(2)
with c1:
    heures = st.number_input("Heures", min_value=0, max_value=40, value=2)
with c2:
    minutes = st.selectbox("Minutes", options=[0, 15, 30, 45], index=0)
duree = heures_entiere_et_minutes(heures, minutes)

st.subheader("😌 Tolérance digestive")
digestif = st.slider("Tolérance digestive (0 = très sensible, 10 = aucune gêne)", 0, 10, 8)
inconfort = st.slider("Historique d’inconfort digestif (0 = jamais, 10 = fréquent)", 0, 10, 2)

# ---------- CALCUL DU SCORE ----------
w_duree, w_rpe, w_poids, w_temp, w_dig, w_sud, w_inconf = 0.30, 0.30, 0.15, 0.10, 0.10, 0.03, 0.02

# Normalisations 0–1
S_duree = clamp(duree / 8, 0, 1)
S_rpe = clamp((rpe - 1) / 9, 0, 1)
S_poids = clamp((poids - 40) / 80, 0, 1)
S_temp = clamp((temperature - 5) / 35, 0, 1)
S_sud = sudation / 10
S_dig = digestif / 10
S_inconf = 1 - (inconfort / 10)

S = (
    w_duree * S_duree +
    w_rpe * S_rpe +
    w_poids * S_poids +
    w_temp * S_temp +
    w_dig * S_dig +
    w_sud * S_sud +
    w_inconf * S_inconf
)
S = clamp(S, 0, 1)

# Amplification de l'effet du RPE : transformation exponentielle
S = S ** 1.3

# Effet digestif plus marqué
facteur_digestif = 0.7 + 0.3 * (S_dig**1.5)
S *= facteur_digestif
S = clamp(S, 0, 1)

# ---------- MAPPING 15–150 g/h ----------
LOW, HIGH = 15, 150
mid = LOW + (HIGH - LOW) * S
band = 15
g_min = clamp(mid - band, LOW, HIGH)
g_max = clamp(mid + band, LOW, HIGH)

# ---------- VISUALISATION ----------
st.header("📊 Résultats")
st.metric("Durée totale", f"{heures}h {minutes:02d}min")
st.metric("Score global", f"{S*100:.0f}/100")
st.progress(S)

st.subheader("🎯 Recommandation en glucides")
st.write(f"**Min : {g_min:.0f} g/h** | **Cible : {mid:.0f} g/h** | **Max : {g_max:.0f} g/h**")

st.markdown(
    f"🧪 **Ratio glucose : fructose recommandé : 1 : 1**  → soit environ "
    f"**{mid/2:.0f} g de glucose + {mid/2:.0f} g de fructose** par heure."
)

# ---------- GRAPHIQUE ----------
durations = np.linspace(0.5, 40, 80)
rpe_values = np.linspace(1, 10, 10)

fig, ax = plt.subplots(figsize=(6, 4))
for r in [2, 4, 6, 8, 10]:
    S_d = np.clip(durations / 8, 0, 1)
    S_i = np.clip((r - 1) / 9, 0, 1)
    S_sim = (w_duree*S_d + w_rpe*S_i)
    S_sim = np.clip(S_sim ** 1.3, 0, 1)
    g_sim = LOW + (HIGH - LOW) * S_sim
    ax.plot(durations, g_sim, label=f"RPE {r}/10")

ax.set_title("Évolution des besoins glucidiques (g/h)")
ax.set_xlabel("Durée (heures)")
ax.set_ylabel("Glucides (g/h)")
ax.set_xlim(0, 40)
ax.set_ylim(0, 160)
ax.legend()
st.pyplot(fig)

# ---------- FOOTER ----------
st.markdown("---")
st.markdown(
    """
    **Interprétation :**
    - 15–40 g/h → effort court, faible intensité ou faible tolérance  
    - 60–90 g/h → zone optimale pour la majorité des marathoniens  
    - 100–150 g/h → ultra-endurance ou athlète entraîné à l’ingestion  
    """
)
st.caption(
    "Sources : Burke et al. 2021 • Jeukendrup 2014 • Stellingwerff 2019.  "
    "Ratio 1 : 1 glucose/fructose pour une absorption équilibrée et une tolérance maximale."
)

