import streamlit as st
import pandas as pd
import ast
import random

# --- CONFIGURATION LOOK & FEEL ---
st.set_page_config(page_title="CinéQuiz Pro", page_icon="🎬", layout="wide")

# CSS personnalisé pour un look "Waoh"
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #e50914;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff0a16;
        border: none;
    }
    .clue-card {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #e50914;
        margin-bottom: 10px;
    }
    .result-win {
        color: #00ff00;
        font-size: 30px;
        font-weight: bold;
        text-align: center;
    }
    .result-lose {
        color: #ff4b4b;
        font-size: 30px;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- CHARGEMENT ---
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

    credits['char'], credits['actor'] = zip(*credits['cast'].apply(get_cast))
    credits['director'] = credits['crew'].apply(get_director)

    df = pd.merge(movies[['title', 'release_date', 'genre_list']], 
                  credits[['title', 'char', 'actor', 'director']], on='title')
    return df

df = load_and_clean_data()

# --- ETAT DU JEU ---
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

# --- UI ---
st.title("🍿 CinéQuiz : Le Défi des 5000 Films")

if not st.session_state.game_active:
    st.markdown("### Prêt à tester votre culture cinéma ?")
    st.write("Le film est choisi au hasard. Plus vous échouez, plus les indices deviennent précis.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🟢 FACILE (10 essais)"): start_game("Facile")
    with col2:
        if st.button("🟡 MOYEN (5 essais)"): start_game("Moyen")
    with col3:
        if st.button("🔴 DIFFICILE (3 essais)"): start_game("Difficile")

else:
    film = st.session_state.target
    
    # Header du jeu
    col_score, col_progress = st.columns([1, 3])
    with col_score:
        st.metric("Vies", st.session_state.tries)
    with col_progress:
        prog = st.session_state.tries / st.session_state.max_tries
        st.write("Santé du joueur")
        st.progress(prog)

    st.markdown("---")

    # Affichage des indices façon "Cartes"
    st.markdown("#### 🔍 Indices débloqués")
    shown = st.session_state.max_tries - st.session_state.tries
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='clue-card'>🎬 <b>Réalisateur :</b><br>{film['director']}</div>", unsafe_allow_html=True)
        if shown >= 2:
            st.markdown(f"<div class='clue-card'>🎭 <b>Acteur principal :</b><br>{film['actor']}</div>", unsafe_allow_html=True)
        if shown >= 4:
            st.markdown(f"<div class='clue-card'>🔡 <b>Première lettre :</b><br>{film['title'][0]}</div>", unsafe_allow_html=True)

    with c2:
        if shown >= 1:
            st.markdown(f"<div class='clue-card'>📅 <b>Année :</b><br>{str(film['release_date'])[:4]}</div>", unsafe_allow_html=True)
        if shown >= 3:
            st.markdown(f"<div class='clue-card'>🎭 <b>Rôle :</b><br>{film['char']}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Input avec Suggestion (Plus interactif !)
    st.write("Entrez le titre du film :")
    user_guess = st.selectbox("Tapez ou choisissez le film :", [""] + sorted(df['title'].tolist()), label_visibility="collapsed")
    
    col_v, col_a = st.columns([1,1])
    with col_v:
        if st.button("🚀 VALIDER"):
            if user_guess.lower().strip() == film['title'].lower().strip():
                st.balloons()
                st.session_state.msg = ("win", f"🏆 INCROYABLE ! C'était bien : {film['title']}")
                st.session_state.game_active = False
                st.rerun()
            else:
                st.session_state.tries -= 1
                if st.session_state.tries <= 0:
                    st.session_state.msg = ("lose", f"💀 DOMMAGE... La réponse était : {film['title']}")
                    st.session_state.game_active = False
                    st.rerun()
                else:
                    st.toast("Mauvaise réponse ! Un indice a été ajouté.", icon="❌")

    with col_a:
        if st.button("🏳️ ABANDONNER"):
            st.session_state.game_active = False
            st.rerun()

# Affichage des messages de fin
if st.session_state.msg:
    type_msg, texte = st.session_state.msg
    if type_msg == "win":
        st.markdown(f"<p class='result-win'>{texte}</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='result-lose'>{texte}</p>", unsafe_allow_html=True)
    
    if st.button("🔄 REJOUER UNE PARTIE"):
        st.session_state.msg = None
        st.rerun()
