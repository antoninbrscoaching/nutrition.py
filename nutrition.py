import streamlit as st

st.set_page_config(page_title="Calculateur Nutrition Course", page_icon="🏃‍♂️", layout="centered")

st.title("🏃‍♂️ Calculateur de Nutrition de Course")
st.markdown("Ce calculateur estime tes besoins en glucides par heure selon ton profil et ta course.")

# --- Saisie des données utilisateur ---
st.header("📋 Profil de l'athlète")
age = st.number_input("Âge (ans)", min_value=10, max_value=90, value=30)
sexe = st.selectbox("Sexe", ["Homme", "Femme"])
poids = st.number_input("Poids (kg)", min_value=30.0, max_value=150.0, value=70.0)
taille = st.number_input("Taille (cm)", min_value=120.0, max_value=220.0, value=175.0)
fc_max = st.number_input("Fréquence cardiaque max (bpm)", min_value=120, max_value=220, value=190)

st.header("🏁 Détails de la course")
distance = st.number_input("Distance (km)", min_value=1.0, max_value=300.0, value=21.1)
duree = st.number_input("Durée de la course (heures)", min_value=0.5, max_value=24.0, value=1.5)
fc_moy = st.number_input("Fréquence cardiaque moyenne (bpm)", min_value=60, max_value=fc_max, value=160)

# --- Calculs ---
vitesse = distance / duree
depense_kcal_h = poids * vitesse  # estimation simple
intensite = fc_moy / fc_max

if intensite < 0.7:
    part_glucides = 0.60
elif intensite < 0.8:
    part_glucides = 0.70
else:
    part_glucides = 0.85

glucides_g_h = (depense_kcal_h * part_glucides) / 4

# --- Affichage des résultats ---
st.header("📊 Résultats")
st.metric("Vitesse moyenne", f"{vitesse:.1f} km/h")
st.metric("Dépense énergétique estimée", f"{depense_kcal_h:.0f} kcal/h")
st.metric("Intensité", f"{intensite*100:.0f} % de la FCmax")
st.metric("Glucides recommandés", f"{glucides_g_h:.0f} g/h")

# --- Recommandation pratique ---
st.subheader("💡 Recommandation pratique")
if glucides_g_h < 50:
    st.info("Objectif faible : vise **30–50 g/h**, surtout via boisson énergétique.")
elif glucides_g_h < 70:
    st.success("Objectif modéré : vise **60–70 g/h**, en mixant gels + boisson.")
else:
    st.warning("Objectif élevé : vise **80–90 g/h**, avec ratio glucose:fructose **2:1**.")

st.markdown("---")
st.caption("Calcul basé sur une estimation moyenne : ajuster selon ta tolérance digestive et ton expérience.")
