import streamlit as st
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Calculateur & Simulateur Nutrition", page_icon="🏃‍♂️", layout="centered")

st.title("🏃‍♂️ Calculateur complet de nutrition + simulateur intelligent")
st.markdown(
    """
    Calcule ton besoin en **glucides (g/h)** selon ton profil,  
    puis simule une **stratégie nutritionnelle détaillée toutes les 20 minutes**, 
    avec suivi du **ratio glucose : fructose**.
    """
)

# ---------------- UTILS ----------------
def clamp(x, lo, hi): return max(lo, min(hi, x))
def heures_entiere_et_minutes(h, m): return h + (m / 60)

# ---------------- PARTIE 1 – CALCUL PHYSIO ----------------
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
    heures = st.number_input("Heures", min_value=0, max_value=40, value=3)
with c2:
    minutes = st.selectbox("Minutes", options=[0, 15, 30, 45], index=0)
duree = heures_entiere_et_minutes(heures, minutes)

# --- Calcul de la cible
S_duree = clamp(duree / 8, 0, 1)
S_rpe = clamp((rpe - 1) / 9, 0, 1)
S_poids = clamp((poids - 50) / 40, 0, 1)
S_temp = clamp((temperature - 10) / 25, 0, 1)
S_sud = sudation / 10
S_dig = digestif / 10
S_inconf = 1 - (inconfort / 10)

w_duree, w_rpe, w_mass, w_temp, w_sud, w_dig, w_inconf = 0.30, 0.30, 0.15, 0.10, 0.05, 0.07, 0.03
S = (w_duree*S_duree + w_rpe*S_rpe + w_mass*S_poids + w_temp*S_temp +
     w_sud*S_sud + w_dig*S_dig + w_inconf*S_inconf)
S = clamp(S, 0, 1)
S = S**1.3
facteur_digestif = 0.7 + 0.3 * (S_dig ** 1.5)
S *= facteur_digestif
S = clamp(S, 0, 1)

LOW, HIGH = 15, 150
mid = LOW + (HIGH - LOW) * S
band = 15
g_min = clamp(mid - band, LOW, HIGH)
g_max = clamp(mid + band, LOW, HIGH)

st.header("📊 Recommandation de glucides")
st.metric("Durée totale", f"{heures}h {minutes:02d}min")
st.progress(S)
st.write(f"**Min : {g_min:.0f} g/h | Cible : {mid:.0f} g/h | Max : {g_max:.0f} g/h**")

st.markdown("---")

# ---------------- PARTIE 2 – SIMULATEUR ----------------
st.header("🥤 Simulateur nutritionnel (par produit total sur la course)")

st.markdown("Renseigne **ce que tu vas consommer sur toute la course** (pas par heure).")

col1, col2, col3 = st.columns(3)
with col1:
    gel_total = st.number_input("Nombre total de gels", 0, 50, 6)
    gel_glucides = st.number_input("Glucides/gel (g)", 10, 50, 25)
    gel_ratio = st.slider("Ratio glucose/fructose (gel)", 0.5, 2.0, 1.0, 0.1)
with col2:
    boisson_total = st.number_input("Nombre total de bidons (500 ml)", 0, 20, 4)
    boisson_glucides = st.number_input("Glucides/bidon (g)", 10, 60, 30)
    boisson_ratio = st.slider("Ratio glucose/fructose (boisson)", 0.5, 2.0, 1.0, 0.1)
with col3:
    barre_total = st.number_input("Nombre total de barres", 0, 20, 1)
    barre_glucides = st.number_input("Glucides/barre (g)", 10, 60, 40)
    barre_ratio = st.slider("Ratio glucose/fructose (barre)", 0.5, 2.0, 1.0, 0.1)

# --- Fonctions pour ratio
def calc_ratio_parts(ratio):
    glu_part = ratio / (1 + ratio)
    fru_part = 1 / (1 + ratio)
    return glu_part, fru_part

glu_gel, fru_gel = calc_ratio_parts(gel_ratio)
glu_boisson, fru_boisson = calc_ratio_parts(boisson_ratio)
glu_barre, fru_barre = calc_ratio_parts(barre_ratio)

# --- Totaux sur la course
glu_total = (gel_total * gel_glucides * glu_gel +
             boisson_total * boisson_glucides * glu_boisson +
             barre_total * barre_glucides * glu_barre)
fru_total = (gel_total * gel_glucides * fru_gel +
             boisson_total * boisson_glucides * fru_boisson +
             barre_total * barre_glucides * fru_barre)
total_glucides = glu_total + fru_total
glucides_h = total_glucides / duree if duree > 0 else 0
ratio_global = glu_total / fru_total if fru_total > 0 else np.nan

# --- Ratio qualité
if 0.8 <= ratio_global <= 1.2:
    ratio_msg = "✅ Excellent ratio, absorption optimisée."
elif ratio_global < 0.8:
    ratio_msg = "⚠️ Ratio trop riche en fructose : risque digestif."
else:
    ratio_msg = "⚠️ Ratio trop riche en glucose : absorption limitée."

# --- Stratégie toutes les 20 minutes
nb_intervalles = int((duree * 60) / 20)
gels_h = gel_total / duree
boissons_h = boisson_total / duree
barres_h = barre_total / duree

# --- Génération plan d’exemple
plan = []
for i in range(nb_intervalles):
    temps = i * 20
    if i % int(60/20) == 0 and gels_h > 0:
        plan.append(f"🕒 {temps} min → 1 gel")
    elif i % int(60/20*1.5) == 0 and boissons_h > 0:
        plan.append(f"🕒 {temps} min → quelques gorgées de boisson")
    elif i % int(60/20*3) == 0 and barres_h > 0:
        plan.append(f"🕒 {temps} min → 1/2 barre")

# ---------------- RÉSULTATS ----------------
st.subheader("📋 Résumé de ta stratégie")
st.write(f"- Total glucides : **{total_glucides:.0f} g** sur {duree:.2f} h")
st.write(f"- Moyenne : **{glucides_h:.0f} g/h** (objectif {mid:.0f} g/h)")
st.write(f"- Ratio global glucose : fructose ≈ **{ratio_global:.2f} : 1**")
st.info(ratio_msg)

# Comparaison à la cible
ecart = glucides_h - mid
if abs(ecart) < 5:
    st.success("✅ Ta stratégie correspond à la recommandation.")
elif ecart > 0:
    st.warning(f"⚠️ Tu es à +{ecart:.0f} g/h au-dessus de la cible — prudence sur la tolérance.")
else:
    st.info(f"ℹ️ Tu es à -{abs(ecart):.0f} g/h sous la cible — prévois un peu plus d’apport.")

st.markdown("### 🗓️ Exemple de plan de course (toutes les 20 min)")
for ligne in plan:
    st.write(ligne)

st.markdown("---")
st.caption(
    "Basé sur Jeukendrup (2014), Burke (2021), Stellingwerff (2019). "
    "Un ratio glucose:fructose idéal se situe entre 0.8:1 et 1.2:1 pour une absorption optimale sans inconfort."
)
