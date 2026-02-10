import streamlit as st
import pandas as pd
import ast
import random

# --- CONFIGURATION ---
st.set_page_config(page_title="🎬 CinéMaster Elite", page_icon="🔥", layout="wide")

# CSS HYPER-MODERNE (Effets Glassmorphism & Neon)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@500;700&display=swap');

    .stApp {
        background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
    }

    /* Titre Cinéma */
    .title-text {
        font-family: 'Bebas Neue', cursive;
        font-size: 80px;
        color: #FFD700;
        text-align: center;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        margin-bottom: 0px;
    }

    /* Cartes Indices Ultra-Stylisées */
    .clue-card {
        font-family: 'Rajdhani', sans-serif;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 210, 255, 0.3);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        transition: all 0.4s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .clue-card:hover {
        border-color: #00d2ff;
        box-shadow: 0 0 25px rgba(0, 210, 255, 0.4);
        transform: scale(1.02);
    }

    /* Boutons custom */
    div.stButton > button {
        font-family: 'Rajdhani', sans-serif;
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: black !important;
        font-weight: 800;
        border: none;
        border-radius: 8px;
        padding: 15px 30px;
        font-size: 18px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 20px #FFD700;
        transform: translateY(-2px);
    }

    /* Barre de progression Néon */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #FF0000 , #FFD700);
    }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND (Identique & Robuste) ---
@st.cache_data
def load_data():
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
            return "Non disponible"
        except: return "Inconnu"

    c['char'], c['actor'] = zip(*c['cast'].apply(lambda x: clean(x, 'cast')))
    c['director'] = c['crew'].apply(lambda x: clean(x, 'dir'))
    m['genre_list'] = m['genres'].apply(lambda x: clean(x, 'gen'))
    
    return pd.merge(m[['title', 'release_date', 'genre_list']], 
                  c[['title', 'char', 'actor', 'director']], on='title')

df = load_data()

# --- INITIALISATION ---
if 'active' not in st.session_state: st.session_state.active = False

def start(d):
    st.session_state.target = df.sample(1).iloc[0]
    st.session_state.tries = {"Facile": 10, "Moyen": 5, "Difficile": 3}[d]
    st.session_state.max = st.session_state.tries
    st.session_state.active = True
    st.session_state.end = False

# --- INTERFACE ---
st.markdown("<h1 class='title-text'>CINÉMASTER ELITE</h1>", unsafe_allow_html=True)

if not st.session_state.active:
    st.markdown("<p style='text-align:center; font-size:20px;'>L'expérience ultime de culture cinématographique.</p>", unsafe_allow_html=True)
    _, c, _ = st.columns([1,2,1])
    with c:
        d = st.select_slider("", options=["Facile", "Moyen", "Difficile"])
        if st.button("LANCER LE DÉFI"): start(d)
else:
    f = st.session_state.target
    err = st.session_state.max - st.session_state.tries
    
    # HUD de Jeu
    c1, c2 = st.columns([1,4])
    c1.metric("VIES", st.session_state.tries)
    c2.progress(st.session_state.tries / st.session_state.max)

    # Grille d'indices débloqués
    cols = st.columns(3)
    indices = [
        ("🎬 RÉALISATEUR", f['director'], 0),
        ("📅 ANNÉE", str(f['release_date'])[:4], 1),
        ("🎭 GENRES", f['genre_list'], 2),
        ("🌟 STAR", f['actor'], 3),
        ("👤 RÔLE", f['char'], 4),
        ("🔡 INITIALE", f['title'][0], 5)
    ]

    for i, (label, val, limit) in enumerate(indices):
        with cols[i % 3]:
            if err >= limit:
                st.markdown(f"<div class='clue-card'><small>{label}</small><br><b style='color:#00d2ff; font-size:1.2rem;'>{val}</b></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='clue-card' style='opacity:0.3;'><small>{label}</small><br>🔒 Verrouillé</div>", unsafe_allow_html=True)

    # Zone de Saisie
    st.markdown("<br>", unsafe_allow_html=True)
    guess = st.selectbox("IDENTIFIEZ LE FILM :", [""] + sorted(df['title'].tolist()))
    
    col_v, col_a = st.columns(2)
    if col_v.button("VÉRIFIER"):
        if guess.lower().strip() == f['title'].lower().strip():
            st.balloons()
            st.success(f"⭐ GÉNIE ! C'était : {f['title']}")
            st.session_state.active = False
            if st.button("REJOUER"): st.rerun()
        else:
            st.session_state.tries -= 1
            if st.session_state.tries <= 0:
                st.error(f"⌛ FIN DE PARTIE. La réponse était : {f['title']}")
                st.session_state.active = False
                if st.button("RÉESSAYER"): st.rerun()
            else:
                st.toast("Ce n'est pas le bon film...", icon="🚫")

    if col_a.button("ABANDONNER"):
        st.session_state.active = False
        st.rerun()
