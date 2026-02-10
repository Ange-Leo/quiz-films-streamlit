import streamlit as st
import pandas as pd
import ast
import random

# --- CONFIGURATION LOOK & FEEL ---
st.set_page_config(page_title="CinéMaster Quiz", page_icon="🎬", layout="wide")

# CSS "WAOH" : Dégradés, Néons et Cartes Modernes
st.markdown("""
    <style>
    /* Fond dégradé moderne */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
    }
    
    /* Titre stylisé */
    .main-title {
        font-size: 3.5rem !important;
        font-weight: 900;
        text-align: center;
        background: -webkit-linear-gradient(#00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }

    /* Cartes d'indices */
    .clue-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(4px);
        margin-bottom: 15px;
        transition: transform 0.3s ease;
    }
    .clue-box:hover {
        transform: translateY(-5px);
        border: 1px solid #00d2ff;
    }

    /* Boutons personnalisés */
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
        border-radius: 50px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.6);
        transform: scale(1.05);
    }

    /* Message de succès/défaite */
    .big-msg {
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
    }
    .win { background: rgba(0, 255, 127, 0.2); border: 2px solid #00ff7f; color: #00ff7f; }
    .lose { background: rgba(255, 75, 75, 0.2); border: 2px solid #ff4b4b; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- CHARGEMENT DES DONNÉES (Identique) ---
@st.cache_data
def load_and_clean_data():
    movies = pd.read_csv('movies.csv')
    credits = pd.read_parquet('credits.parquet')
    
    def get_cast(x):
        try:
            l = ast.literal_eval(x)
            if len(l) > 0: return l[0]['character'], l[0]['name']
            return "Inconnu", "Inconnu"
        except: return "Inconnu", "Inconnu"

    def get_director(x):
        try:
            l = ast.literal_eval(x)
            for i in l:
                if i['job'] == 'Director': return i['name']
            return "Inconnu"
        except: return "Inconnu"

    def get_genres(x):
        try:
            l = ast.literal_eval(x)
            return ", ".join([g['name'] for g in l])
        except: return "Inconnu"

    credits['char'], credits['actor'] = zip(*credits['cast'].apply(get_cast))
    credits['director'] = credits['crew'].apply(get_director)
    movies['genre_list'] = movies['genres'].apply(get_genres)

    df = pd.merge(movies[['title', 'release_date', 'genre_list']], 
                  credits[['title', 'char', 'actor', 'director']], on='title')
    return df

df = load_and_clean_data()

# --- LOGIQUE DU JEU ---
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'msg' not in st.session_state:
    st.session_state.msg = None

def start_game(diff):
    target = df.sample(1).iloc[0]
    st.session_state.target = target
    st.session_state.tries = {"Facile": 10, "Moyen": 5, "Difficile": 3}[diff]
    st.session_state.max_tries = st.session_state.tries
    st.session_state.game_active = True
    st.session_state.msg = None

# --- INTERFACE ---
st.markdown("<h1 class='main-title'>🎬 CINÉMASTER QUIZ</h1>", unsafe_allow_html=True)

if not st.session_state.game_active:
    st.markdown("<div style='text-align: center; margin-bottom: 2rem;'><h3>Prêt pour le défi ? Sélectionnez votre niveau :</h3></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("🟢 FACILE (10 Vies)"): start_game("Facile")
    with c2: 
        if st.button("🟡 MOYEN (5 Vies)"): start_game("Moyen")
    with c3: 
        if st.button("🔴 DIFFICILE (3 Vies)"): start_game("Difficile")

else:
    film = st.session_state.target
    
    # Barre de progression dynamique
    col_v, col_p = st.columns([1, 4])
    with col_v:
        st.write(f"❤️ **Vies : {st.session_state.tries}**")
    with col_p:
        pct = st.session_state.tries / st.session_state.max_tries
        st.progress(pct)

    st.markdown("### 🔍 VOS INDICES")
    shown = st.session_state.max_tries - st.session_state.tries
    
    # Grille d'indices
    idx1, idx2 = st.columns(2)
    with idx1:
        st.markdown(f"<div class='clue-box'>🎥 <b>Réalisateur</b><br><span style='font-size: 1.2rem; color: #00d2ff;'>{film['director']}</span></div>", unsafe_allow_html=True)
        if shown >= 2:
            st.markdown(f"<div class='clue-box'>🌟 <b>Star</b><br><span style='font-size: 1.2rem; color: #00d2ff;'>{film['actor']}</span></div>", unsafe_allow_html=True)
        if shown >= 4:
            st.markdown(f"<div class='clue-box'>🔡 <b>Initiale</b><br><span style='font-size: 1.2rem; color: #00d2ff;'>{film['title'][0]}</span></div>", unsafe_allow_html=True)

    with idx2:
        if shown >= 1:
            st.markdown(f"<div class='clue-box'>📅 <b>Sortie</b><br><span style='font-size: 1.2rem; color: #00d2ff;'>{str(film['release_date'])[:4]}</span></div>", unsafe_allow_html=True)
        if shown >= 3:
            st.markdown(f"<div class='clue-box'>👤 <b>Personnage</b><br><span style='font-size: 1.2rem; color: #00d2ff;'>{film['char']}</span></div>", unsafe_allow_html=True)
        if shown >= 5:
            st.markdown(f"<div class='clue-box'>🎭 <b>Genres</b><br><span style='font-size: 1.2rem; color: #00d2ff;'>{film['genre_list']}</span></div>", unsafe_allow_html=True)

    # Zone de saisie
    st.markdown("---")
    user_guess = st.selectbox("QUEL EST LE TITRE DU FILM ?", [""] + sorted(df['title'].tolist()))
    
    bv, ba = st.columns(2)
    with bv:
        if st.button("⚡ VÉRIFIER"):
            if user_guess.lower().strip() == film['title'].lower().strip():
                st.balloons()
                st.session_state.msg = ("win", f"🏆 BRAVO ! C'était bien : {film['title']}")
                st.session_state.game_active = False
                st.rerun()
            else:
                st.session_state.tries -= 1
                if st.session_state.tries <= 0:
                    st.session_state.msg = ("lose", f"💀 PERDU ! Le film était : {film['title']}")
                    st.session_state.game_active = False
                    st.rerun()
                else:
                    st.toast(f"Faux ! Il vous reste {st.session_state.tries} vies.", icon="🔥")

    with ba:
        if st.button("🏳️ ABANDONNER"):
            st.session_state.game_active = False
            st.rerun()

# Messages de fin
if st.session_state.msg:
    res_type, res_text = st.session_state.msg
    css_class = "win" if res_type == "win" else "lose"
    st.markdown(f"<div class='big-msg {css_class}'>{res_text}</div>", unsafe_allow_html=True)
    if st.button("🎮 REJOUER"):
        st.session_state.msg = None
        st.rerun()

