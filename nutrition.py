import streamlit as st
import numpy as np
import math

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Calculateur & Plan Nutrition", page_icon="🏃‍♂️", layout="centered")

st.title("🏃‍♂️ Calculateur de nutrition + plan réaliste arrondi + Gut Training")
st.markdown(
    """
    Calcule tes besoins en **glucides (g/h)** et obtiens :
    - un **plan d’ingestion réaliste** toutes les 20 à 30 minutes (arrondi à la minute),  
    - un **plan de gut training progressif** sur 6 semaines pour améliorer la tolérance digestive.
    """
)

# ---------------- UTILS ----------------
def clamp(x, lo, hi): return max(lo, min(hi, x))
def heures_entiere_et_minutes(h, m): return h + (m / 60)
def calc_ratio_parts(ratio):
    glu_part = ratio / (1 + ratio)
    fru_part = 1 / (1 + ratio)
    return glu_part, fru_part

def format_gel_portion(value):
    if value < 0.25: return "une petite lèche de gel"
    elif value < 0.5: return "¼ gel"
    elif value < 0.75: return "½ gel"
    elif value < 1.0: return "¾ gel"
    else: return "1 gel"

def format_barre_portion(value):
    if value < 0.25: return "un petit morceau de barre"
    elif value < 0.5: return "½ barre"
    elif value < 0.75: return "¾ barre"
    else: return "1 barre"

def format_flask_portion(value):
    gorgées = round(value * 10)
    if gorgées <= 1: return "1 gorgée"
    elif gorgées <= 3: return "2-3 gorgées"
    elif gorgées <= 5: return "4-5 gorgées"
    elif gorgées <= 7: return "6-7 gorgées"
    else: return "quelques grandes gorgées (~½ flasque)"

# ---------------- CALCULATEUR ----------------
st.header("📋 Profil & conditions de course")

col1, col2, col3 = st.columns(3)
with col1:
    poids = st.number_input("Poids (kg)", 40.0, 120.0, 70.0)
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
    heures = st.number_input("Heures", 0, 40, 2)
with c2:
    minutes = st.selectbox("Minutes", [0, 15, 30, 45], index=3)
duree = heures_entiere_et_minutes(heures, minutes)

# --- Calcul besoin g/h
S_duree = clamp(duree / 8, 0, 1)
S_rpe = clamp((rpe - 1) / 9, 0, 1)
S_poids = clamp((poids - 50) / 40, 0, 1)
S_temp = clamp((temperature - 10) / 25, 0, 1)
S_sud = sudation / 10
S_dig = digestif / 10
S_inconf = 1 - (inconfort / 10)

S = (
    0.30*S_duree + 0.30*S_rpe + 0.15*S_poids +
    0.10*S_temp + 0.05*S_sud + 0.07*S_dig + 0.03*S_inconf
)
S = clamp(S, 0, 1)**1.3
S *= (0.7 + 0.3*(S_dig**1.5))
S = clamp(S, 0, 1)

LOW, HIGH = 15, 150
mid = LOW + (HIGH - LOW) * S
band = 15
g_min, g_max = clamp(mid - band, LOW, HIGH), clamp(mid + band, LOW, HIGH)

st.header("📊 Recommandation glucides")
st.metric("Durée totale", f"{heures}h {minutes:02d}min")
st.write(f"**Min : {g_min:.0f} g/h | Cible : {mid:.0f} g/h | Max : {g_max:.0f} g/h**")

st.markdown("---")

# ---------------- SIMULATEUR ----------------
st.header("🥤 Stratégie nutritionnelle (total sur la course)")

col1, col2, col3 = st.columns(3)
with col1:
    gel_total = st.number_input("Nombre total de gels", 0, 50, 3)
    gel_glucides = st.number_input("Glucides/gel (g)", 10, 50, 25)
    gel_ratio = st.slider("Ratio glucose/fructose (gel)", 0.5, 2.0, 1.0, 0.1)
with col2:
    boisson_total = st.number_input("Nombre total de flasques (500 ml)", 0, 10, 1)
    boisson_glucides = st.number_input("Glucides/flasque (g)", 10, 60, 30)
    boisson_ratio = st.slider("Ratio glucose/fructose (boisson)", 0.5, 2.0, 1.0, 0.1)
with col3:
    barre_total = st.number_input("Nombre total de barres", 0, 10, 1)
    barre_glucides = st.number_input("Glucides/barre (g)", 10, 60, 40)
    barre_ratio = st.slider("Ratio glucose/fructose (barre)", 0.5, 2.0, 1.0, 0.1)

# --- Ratio global
glu_gel, fru_gel = calc_ratio_parts(gel_ratio)
glu_boisson, fru_boisson = calc_ratio_parts(boisson_ratio)
glu_barre, fru_barre = calc_ratio_parts(barre_ratio)

glu_total = (
    gel_total * gel_glucides * glu_gel +
    boisson_total * boisson_glucides * glu_boisson +
    barre_total * barre_glucides * glu_barre
)
fru_total = (
    gel_total * gel_glucides * fru_gel +
    boisson_total * boisson_glucides * fru_boisson +
    barre_total * barre_glucides * fru_barre
)
total_glucides = glu_total + fru_total
glucides_h = total_glucides / duree if duree > 0 else 0
ratio_global = glu_total / fru_total if fru_total > 0 else np.nan

# Ratio feedback
if 0.8 <= ratio_global <= 1.2:
    ratio_msg = "✅ Excellent ratio (absorption optimale)."
elif ratio_global < 0.8:
    ratio_msg = "⚠️ Trop de fructose (risque digestif)."
else:
    ratio_msg = "⚠️ Trop de glucose (absorption limitée)."

# ---------------- PLAN DYNAMIQUE ARRONDI ----------------
st.header("🕒 Plan nutrition (intervalle arrondi entre 20 et 30 min)")

duree_minutes = duree * 60
nb_intervalles = max(1, round(duree_minutes / 25))
intervalle = round(duree_minutes / nb_intervalles)
intervalle = int(clamp(intervalle, 20, 30))
nb_intervalles = math.ceil(duree_minutes / intervalle)

gel_frac = gel_total / nb_intervalles
boisson_frac = boisson_total / nb_intervalles
barre_frac = barre_total / nb_intervalles

plan = []
for i in range(nb_intervalles):
    temps = int(i * intervalle)
    contenu = []
    if gel_frac > 0:
        contenu.append(format_gel_portion(gel_frac))
    if boisson_frac > 0:
        contenu.append(format_flask_portion(boisson_frac))
    if barre_frac > 0:
        contenu.append(format_barre_portion(barre_frac))
    plan.append(f"⏱️ {int(temps//60)}h{int(temps%60):02d} → " + " + ".join(contenu))

# ---------------- RÉSULTATS ----------------
st.subheader("📋 Résumé global")
st.write(f"- Total glucides : **{total_glucides:.0f} g** sur {duree:.2f} h")
st.write(f"- Moyenne : **{glucides_h:.0f} g/h** (objectif {mid:.0f} g/h)")
st.write(f"- Ratio global glucose : fructose ≈ **{ratio_global:.2f} : 1**")
st.info(ratio_msg)
st.write(f"🕒 Intervalle entre prises : **{intervalle} minutes**")

ecart = glucides_h - mid
if abs(ecart) < 5:
    st.success("✅ Stratégie alignée avec la recommandation.")
elif ecart > 0:
    st.warning(f"⚠️ +{ecart:.0f} g/h au-dessus de la cible — attention à la tolérance.")
else:
    st.info(f"ℹ️ -{abs(ecart):.0f} g/h sous la cible — ajoute un peu d’apport.")

st.markdown("### 📋 Exemple de plan réaliste (toutes les ~20–30 min)")
for ligne in plan:
    st.write(ligne)

# ---------------- GUT TRAINING PLAN ----------------
st.markdown("---")
st.header("🧠 Gut Training – Plan d’adaptation digestive sur 6 semaines")

target = mid  # objectif calculé
start = target * 0.6  # commence à 60 % de la cible
steps = np.linspace(start, target, 6)

st.markdown("### 📆 Progression hebdomadaire vers la tolérance optimale")
for i, g in enumerate(steps, 1):
    st.write(f"**Semaine {i} :** viser environ **{g:.0f} g/h**")
st.caption(
    "Commence à 60 % de la cible pour éviter l'inconfort, puis augmente chaque semaine "
    "jusqu'à la tolérance complète à la semaine 6."
)

st.markdown("---")
st.caption(
    "Basé sur Jeukendrup (2017), Burke (2021) et Stellingwerff (2019). "
    "Intervalle ajusté automatiquement et arrondi à la minute (20–30 min). "
    "Total consommé = quantités prévues exactement."
)
