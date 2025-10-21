import streamlit as st
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Calculateur & Simulateur Nutrition", page_icon="🏃‍♂️", layout="centered")

st.title("🏃‍♂️ Calculateur complet de nutrition + simulateur personnalisé")
st.markdown(
    """
    Calcule ton besoin en **glucides (g/h)** selon ton profil, 
    puis simule ta stratégie nutritionnelle avec un **ratio glucose : fructose** propre à chaque produit.
    """
)

# ---------------- UTILS ----------------
def clamp(x, lo, hi): return max(lo, min(hi, x))
def heures_entiere_et_minutes(h, m): return h + (m / 60)

# ---------------- ENTRÉES PHYSIO ----------------
st.header("📋 Profil & conditions de course")

col1, col2, col3 = st.columns(3)
with col1:
    poids = st.number_input("Poids (kg)", 40.0, 120.0, 70.0, step=0.5)
    rpe = st.slider("Intensité perçue (RPE/10)", 1, 10, 7)
with col2:
    temperature = st.slider("Température (°C)", -5.0, 40.0, 20.0, step=0.5)
    sudation = st.slider("Sudation (0=faible, 10=forte)", 0, 10, 5)
with col3:
    digestif = st.slider("Tolérance digestive (0=sensible, 10=aucune gêne)", 0, 10, 8)
    inconfort = st.slider("Inconfort digestif (0=jamais, 10=souvent)", 0, 10, 2)

st.subheader("⏱ Durée de l'effort")
c1, c2 = st.columns(2)
with c1:
    heures = st.number_input("Heures", min_value=0, max_value=40, value=2)
with c2:
    minutes = st.selectbox("Minutes", options=[0, 15, 30, 45], index=0)
duree = heures_entiere_et_minutes(heures, minutes)

# ---------------- CALCUL PHYSIO ----------------
# Normalisations
S_duree = clamp(duree / 8, 0, 1)
S_rpe = clamp((rpe - 1) / 9, 0, 1)
S_poids = clamp((poids - 50) / 40, 0, 1)
S_temp = clamp((temperature - 10) / 25, 0, 1)
S_sud = sudation / 10
S_dig = digestif / 10
S_inconf = 1 - (inconfort / 10)

# Pondérations
w_duree, w_rpe, w_mass, w_temp, w_sud, w_dig, w_inconf = 0.30, 0.30, 0.15, 0.10, 0.05, 0.07, 0.03
S = (
    w_duree*S_duree +
    w_rpe*S_rpe +
    w_mass*S_poids +
    w_temp*S_temp +
    w_sud*S_sud +
    w_dig*S_dig +
    w_inconf*S_inconf
)
S = clamp(S, 0, 1)
S = S**1.3  # courbe progressive

# Effet digestif
facteur_digestif = 0.7 + 0.3 * (S_dig ** 1.5)
S *= facteur_digestif
S = clamp(S, 0, 1)

# Calcul final g/h
LOW, HIGH = 15, 150
mid = LOW + (HIGH - LOW) * S
band = 15
g_min = clamp(mid - band, LOW, HIGH)
g_max = clamp(mid + band, LOW, HIGH)

# ---------------- AFFICHAGE ----------------
st.header("📊 Recommandation de glucides")
st.metric("Durée totale", f"{heures}h {minutes:02d}min")
st.progress(S)
st.write(f"**Min : {g_min:.0f} g/h | Cible : {mid:.0f} g/h | Max : {g_max:.0f} g/h**")

st.markdown("---")

# ---------------- SIMULATEUR ----------------
st.header("🥤 Simulateur nutritionnel")

st.markdown("Personnalise chaque produit et sa composition en glucose/fructose.")

col1, col2, col3 = st.columns(3)
with col1:
    gel_qte = st.number_input("Gels (unité)", 0, 50, 4)
    gel_glucides = st.number_input("Glucides/gel (g)", 10, 50, 25)
    gel_ratio = st.slider("Ratio glucose/fructose (gel)", 0.5, 2.0, 1.0, 0.1)
with col2:
    boisson_qte = st.number_input("Boissons (500 ml)", 0, 20, 3)
    boisson_glucides = st.number_input("Glucides/boisson (g)", 10, 60, 30)
    boisson_ratio = st.slider("Ratio glucose/fructose (boisson)", 0.5, 2.0, 1.0, 0.1)
with col3:
    barre_qte = st.number_input("Barres (unité)", 0, 20, 1)
    barre_glucides = st.number_input("Glucides/barre (g)", 10, 60, 40)
    barre_ratio = st.slider("Ratio glucose/fructose (barre)", 0.5, 2.0, 1.0, 0.1)

freq = st.selectbox("Fréquence d’ingestion", options=["15 min", "30 min", "45 min", "60 min"], index=1)
freq_min = int(freq.split(" ")[0])
nb_prises = int((duree * 60) / freq_min)

# ---------------- CALCULS SIMULATEUR ----------------
def calc_ratio_parts(ratio):
    """Renvoie proportion glucose/fructose"""
    glu_part = ratio / (1 + ratio)
    fru_part = 1 / (1 + ratio)
    return glu_part, fru_part

# Parts par produit
glu_gel, fru_gel = calc_ratio_parts(gel_ratio)
glu_boisson, fru_boisson = calc_ratio_parts(boisson_ratio)
glu_barre, fru_barre = calc_ratio_parts(barre_ratio)

# Total
total_glucides = (
    (gel_qte * gel_glucides) +
    (boisson_qte * boisson_glucides) +
    (barre_qte * barre_glucides)
) * nb_prises

glucides_h = total_glucides / duree if duree > 0 else 0

# Total glucose et fructose
glu_total = (
    (gel_qte * gel_glucides * glu_gel) +
    (boisson_qte * boisson_glucides * glu_boisson) +
    (barre_qte * barre_glucides * glu_barre)
) * nb_prises

fru_total = (
    (gel_qte * gel_glucides * fru_gel) +
    (boisson_qte * boisson_glucides * fru_boisson) +
    (barre_qte * barre_glucides * fru_barre)
) * nb_prises

# Ratio global
ratio_global = glu_total / fru_total if fru_total > 0 else np.nan

# ---------------- RÉSULTATS ----------------
st.subheader("🔢 Résumé de ta stratégie")
st.write(f"- Nombre de prises : **{nb_prises}** ({freq})")
st.write(f"- Total glucides : **{total_glucides:.0f} g** sur {duree:.2f} h")
st.write(f"- Moyenne : **{glucides_h:.0f} g/h**")
st.write(f"- Ratio global glucose : fructose ≈ **{ratio_global:.2f} : 1**")

# Comparaison à la cible
ecart = glucides_h - mid
if abs(ecart) < 5:
    st.success("✅ Ta stratégie correspond à la recommandation.")
elif ecart > 0:
    st.warning(f"⚠️ Tu es à +{ecart:.0f} g/h au-dessus de la cible — attention à ta tolérance.")
else:
    st.info(f"ℹ️ Tu es à -{abs(ecart):.0f} g/h sous la cible — prévois peut-être un apport supplémentaire.")

st.markdown("---")
st.caption(
    "Modèle basé sur : Jeukendrup (2014), Burke (2021), Stellingwerff (2019).  "
    "Les ratios glucose/fructose permettent d'ajuster la vitesse d'absorption et la tolérance digestive."
)
