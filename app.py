import streamlit as st
import pandas as pd
import ast
import random
import os
from PIL import Image

# --- CONFIGURATION GLOBALE ---
st.set_page_config(page_title="CinéMaster & Flags Hub", page_icon="🎮", layout="wide")

# CSS COMMUN (Look Moderne)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@500;700&display=swap');
    .stApp { background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%); color: white; }
    .title-text { font-family: 'Bebas Neue', cursive; font-size: 60px; color: #FFD700; text-align: center; text-shadow: 0 0 15px rgba(255, 215, 0, 0.4); }
    .clue-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(0, 210, 255, 0.3); border-radius: 12px; padding: 15px; text-align: center; }
    div.stButton > button { background: linear-gradient(45deg, #FFD700, #FFA500); color: black !important; font-weight: bold; border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
st.sidebar.title("🎮 MENU JEUX")
choix_jeu = st.sidebar.radio("Choisissez votre défi :", ["🎬 CinéMaster Elite", "🌍 World Flag Quiz"])
st.sidebar.markdown("---")
st.sidebar.info("Projet développé en Python & Streamlit")

# ==========================================
# FONCTIONS JEU CINÉMA
# ==========================================
@st.cache_data
def load_movie_data():
    m = pd.read_csv('movies.csv')
    c = pd.read_parquet('credits.parquet')
    def clean(x, mode):
        try:
            l = ast.literal_eval(x)
            if mode == 'cast' and len(l) > 0: return l[0]['character'], l[0]['name']
            if mode == 'dir':
                for i in l:
                    if i['job'] == 'Director': return i['name']
            if mode == 'gen': return ", ".join([g['name'] for g in l])
            return "Inconnu"
        except: return "Inconnu"
    c['char'], c['actor'] = zip(*c['cast'].apply(lambda x: clean(x, 'cast')))
    c['director'] = c['crew'].apply(lambda x: clean(x, 'dir'))
    m['genre_list'] = m['genres'].apply(lambda x: clean(x, 'gen'))
    return pd.merge(m[['title', 'release_date', 'genre_list']], c[['title', 'char', 'actor', 'director']], on='title')

# ==========================================
# FONCTIONS JEU DRAPEAUX
# ==========================================
@st.cache_data
def load_flags():
    path = "flags"
    if not os.path.exists(path): return pd.DataFrame()
    fichiers = [f for f in os.listdir(path) if f.startswith("Flag of") and f.lower().endswith('.gif')]
    return pd.DataFrame([{'pays': f.replace("Flag of ", "").replace(".gif", "").strip(), 'fichier': os.path.join(path, f)} for f in fichiers])

# ==========================================
# LOGIQUE D'AFFICHAGE
# ==========================================

if choix_jeu == "🎬 CinéMaster Elite":
    st.markdown("<h1 class='title-text'>CINÉMASTER ELITE</h1>", unsafe_allow_html=True)
    df_m = load_movie_data()
    
    if 'm_active' not in st.session_state: st.session_state.m_active = False
    
    if not st.session_state.m_active:
        col_s = st.columns([1,2,1])[1]
        diff = col_s.select_slider("Difficulté", options=["Facile", "Moyen", "Difficile"])
        if col_s.button("LANCER LE QUIZ CINÉMA"):
            st.session_state.m_target = df_m.sample(1).iloc[0]
            st.session_state.m_tries = {"Facile": 10, "Moyen": 5, "Difficile": 3}[diff]
            st.session_state.m_max = st.session_state.m_tries
            st.session_state.m_active = True
            st.rerun()
    else:
        # (Ici la logique de ton jeu de film que nous avons déjà codée...)
        f = st.session_state.m_target
        st.metric("VIES RESTANTES", st.session_state.m_tries)
        st.markdown(f"<div class='clue-card'>🎬 Réalisateur : {f['director']}</div>", unsafe_allow_html=True)
        guess = st.selectbox("Titre du film ?", [""] + sorted(df_m['title'].tolist()))
        if st.button("VÉRIFIER"):
            if guess.lower() == f['title'].lower():
                st.balloons(); st.success("BRAVO !"); st.session_state.m_active = False
            else:
                st.session_state.m_tries -= 1
                if st.session_state.m_tries <= 0:
                    st.error(f"PERDU ! C'était {f['title']}"); st.session_state.m_active = False
                else: st.toast("Faux !")

elif choix_jeu == "🌍 World Flag Quiz":
    st.markdown("<h1 class='title-text'>WORLD FLAG QUIZ</h1>", unsafe_allow_html=True)
    df_f = load_flags()
    
    if df_f.empty:
        st.warning("⚠️ Dossier 'flags' introuvable. Créez un dossier nommé 'flags' sur GitHub avec vos .gif.")
    else:
        if 'f_target' not in st.session_state:
            target = df_f.sample(1).iloc[0]
            others = df_f[df_f['pays'] != target['pays']].sample(3)
            opts = pd.concat([pd.DataFrame([target]), others])['pays'].tolist()
            random.shuffle(opts)
            st.session_state.f_target = target
            st.session_state.f_opts = opts

        t = st.session_state.f_target
        c1, c2, c3 = st.columns([1,2,1])
        img = Image.open(t['fichier'])
        c2.image(img.rotate(random.choice([0,90,180,270]), expand=True), use_container_width=True)
        
        cols = st.columns(2)
        for i, opt in enumerate(st.session_state.f_opts):
            if cols[i%2].button(opt):
                if opt == t['pays']:
                    st.balloons(); st.success("Gagné !")
                else:
                    st.error(f"Perdu ! C'était {t['pays']}")
                del st.session_state.f_target # Force le rechargement
                st.button("Suivant")
