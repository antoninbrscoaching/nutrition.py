import streamlit as st
import pandas as pd
import datetime
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Calculateur & Simulateur Nutrition Endurance", page_icon="🏃‍♂️", layout="centered")

st.title("🏃‍♂️ Calculateur & Simulateur de Nutrition Endurance")
st.markdown(
    """
    Cet outil estime tes besoins en **glucides (g/h)** et te permet de **simuler ta stratégie nutritionnelle**
    pendant la course.  
    Il prend en compte ton **gut training** (entraînement digestif) et enregistre chaque session.
    """
)

DATA_FILE = "historique_courses.csv"

# ---------------- UTILS ----------------
def clamp(x, lo, hi): return max(lo, min(hi, x))
def heures_entiere_et_minutes(h, m): return h + (m / 60)
def load_history():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["date", "nom", "poids", "duree_h", "rpe", "digestif", "objectif_g_h"])

def save_session(nom, poids, duree_h, rpe, digestif, objectif):
    df = load_history()
    df.loc[len(df)] = [datetime.date.today(), nom, poids, duree_h, rpe, digestif, objectif]
    df.to_csv(DATA_FILE, index=False)

# ---------------- ENTRÉES ----------------
st.header("📋 Profil de l'athlète et course")

nom = st.text_input("Nom de la course / séance", "Ex : Marathon Nice-Cannes")
poids = st.slider("Poids (kg)", 40, 120, 70, 1)

col1, col2 = st.columns(2)
with col1:
    rpe = st.slider("Intensité perçue (RPE / 10)", 1, 10, 7)
with col2:
    digestif = st.slider("Tolérance digestive (0 = très sensible, 10 = aucune gêne)", 0, 10, 8)

col3, col4 = st.columns(2)
with col3:
    heures = st.number_input("Heures", min_value=0, max_value=40, value=2)
with col4:
    minutes = st.selectbox("Minutes", options=[0, 15, 30, 45], index=0)
duree_h = heures_entiere_et_minutes(heures, minutes)

# ---------------- CALCUL GLUCIDES ----------------
LOW, HIGH = 15, 150

S_duree = clamp(duree_h / 8, 0, 1)
S_rpe = clamp((rpe - 1) / 9, 0, 1)
S_poids = clamp((poids - 40) / 80, 0, 1)
S_dig = digestif / 10

# pondération globale
S = 0.35 * S_duree + 0.35 * S_rpe + 0.15 * S_poids + 0.15 * S_dig
S = S ** 1.2
facteur_digestif = 0.7 + 0.3 * (S_dig ** 1.5)
S *= facteur_digestif
S = clamp(S, 0, 1)

objectif_g_h = LOW + (HIGH - LOW) * S

st.header("📊 Résultat calculé")
st.metric("Recommandation glucides", f"{objectif_g_h:.0f} g/h")
st.markdown(f"**Ratio recommandé glucose : fructose = 1 : 1** → environ **{objectif_g_h/2:.0f} g** de chaque par heure.")

# ---------------- SIMULATEUR ----------------
st.header("🥤 Simulateur de stratégie nutritionnelle")

st.markdown("Indique ce que tu comptes consommer pendant la course :")

col1, col2, col3 = st.columns(3)
with col1:
    gel = st.number_input("Gel (25 g CHO/unité)", 0, 50, 4)
with col2:
    boisson = st.number_input("Boisson (30 g CHO/500ml)", 0, 20, 3)
with col3:
    barre = st.number_input("Barre (40 g CHO/unité)", 0, 20, 1)

freq = st.selectbox("Fréquence d’ingestion", options=["15 min", "30 min", "45 min", "60 min"], index=1)

# équivalence temps en minutes
freq_min = int(freq.split(" ")[0])
nb_prises = int((duree_h * 60) / freq_min)
total_glucides = (gel * 25 + boisson * 30 + barre * 40) * nb_prises
glucides_h = total_glucides / duree_h

st.subheader("🔢 Simulation de ton plan")
st.write(f"- Nombre total de prises : **{nb_prises}**")
st.write(f"- Apport total prévu : **{total_glucides:.0f} g** sur {duree_h:.2f} h")
st.write(f"- Moyenne : **{glucides_h:.0f} g/h**")

# comparaison
ecart = glucides_h - objectif_g_h
if abs(ecart) < 5:
    st.success("✅ Ta stratégie est bien calée avec la recommandation !")
elif ecart > 0:
    st.warning(f"⚠️ Tu dépasses la cible de +{ecart:.0f} g/h. Vérifie ta tolérance.")
else:
    st.info(f"ℹ️ Tu es en dessous de la cible ({abs(ecart):.0f} g/h manquants).")

# ---------------- GUT TRAINING ----------------
st.header("🧠 Gut training (entraînement digestif)")

history = load_history()
if not history.empty:
    st.write("Historique des sessions enregistrées :")
    st.dataframe(history.tail(5))

gut_factor = 1.0
if st.checkbox("Activer le mode Gut Training"):
    gut_factor = 1.03
    st.markdown("💪 Objectif : +3 % de capacité digestive sur cette course.")

objectif_g_h *= gut_factor
objectif_g_h = clamp(objectif_g_h, 15, 160)

# ---------------- SAUVEGARDE ----------------
if st.button("💾 Enregistrer cette session"):
    save_session(nom, poids, duree_h, rpe, digestif, objectif_g_h)
    st.success(f"Séance '{nom}' enregistrée avec un objectif de {objectif_g_h:.0f} g/h.")

st.caption("Les données sont sauvegardées dans le fichier `historique_courses.csv` dans le dossier courant.")
