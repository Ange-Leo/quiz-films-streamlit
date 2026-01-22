import streamlit as st
import pandas as pd
import ast
import random

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Le Jeu des 5000 Films", page_icon="🎬", layout="centered")

# --- FONCTIONS DE PRÉPARATION DES DONNÉES ---
@st.cache_data # Cette fonction ne s'exécute qu'une seule fois pour gagner du temps
def load_and_clean_data():
    # Chargement
    movies = pd.read_csv('movies.csv')
    credits = pd.read_parquet('credits.parquet')
    
    # Nettoyage et Extraction
    def get_cast(x):
        try:
            l = ast.literal_eval(x)
            if len(l) > 0: return l[0]['character'], l[0]['name']
            return "NA", "NA"
        except: return "NA", "NA"

    def get_director(x):
        try:
            l = ast.literal_eval(x)
            for i in l:
                if i['job'] == 'Director': return i['name']
            return "NA"
        except: return "NA"

    def get_genres(x):
        try:
            l = ast.literal_eval(x)
            return ", ".join([g['name'] for g in l])
        except: return "NA"

    credits['char'], credits['actor'] = zip(*credits['cast'].apply(get_cast))
    credits['director'] = credits['crew'].apply(get_director)
    movies['genre_list'] = movies['genres'].apply(get_genres)

    # Fusion
    df = pd.merge(movies[['title', 'release_date', 'runtime', 'genre_list', 'budget']], 
                  credits[['title', 'char', 'actor', 'director']], on='title')
    return df

# --- INITIALISATION ---
df = load_and_clean_data()

# Utilisation du Session State pour garder les infos même quand la page se rafraîchit
if 'game_active' not in st.session_state:
    st.session_state.game_active = False

def start_game(diff):
    target = df.sample(1).iloc[0]
    st.session_state.target = target
    st.session_state.tries = {"Facile": 10, "Moyen": 5, "Difficile": 3}[diff]
    st.session_state.max_tries = st.session_state.tries
    st.session_state.game_active = True
    st.session_state.won = False
    st.session_state.msg = ""

# --- INTERFACE UTILISATEUR ---
st.title("🎬 Devinez le Film !")
st.markdown("---")

if not st.session_state.game_active:
    st.subheader("Choisissez votre difficulté pour commencer :")
    col1, col2, col3 = st.columns(3)
    if col1.button("🟢 Facile"): start_game("Facile")
    if col2.button("🟡 Moyen"): start_game("Moyen")
    if col3.button("🔴 Difficile"): start_game("Difficile")

else:
    film = st.session_state.target
    
    # Affichage des indices progressifs
    st.subheader(f"Tentatives restantes : {st.session_state.tries}")
    
    # Liste des indices (on en montre plus selon le nombre d'erreurs)
    shown_indices = st.session_state.max_tries - st.session_state.tries
    
    with st.expander("📌 Indices disponibles", expanded=True):
        st.write(f"**Réalisateur :** {film['director']}")
        if shown_indices >= 1: st.write(f"**Année de sortie :** {str(film['release_date'])[:4]}")
        if shown_indices >= 2: st.write(f"**Genres :** {film['genre_list']}")
        if shown_indices >= 3: st.write(f"**Acteur principal :** {film['actor']}")
        if shown_indices >= 4: st.write(f"**Personnage :** {film['char']}")
        if shown_indices >= 5: st.write(f"**Première lettre :** {film['title'][0]}")

    # Formulaire de réponse
    with st.form(key='guess_form', clear_on_submit=True):
        user_guess = st.text_input("Titre du film :")
        submit = st.form_submit_button("Valider la réponse")

    if submit:
        if user_guess.lower().strip() == film['title'].lower().strip():
            st.session_state.won = True
            st.session_state.game_active = False
            st.balloons()
            st.success(f"🏆 GAGNÉ ! C'était bien : **{film['title']}**")
            if st.button("Rejouer"): st.rerun()
        else:
            st.session_state.tries -= 1
            if st.session_state.tries <= 0:
                st.error(f"💀 PERDU... Le film était : **{film['title']}**")
                st.session_state.game_active = False
                if st.button("Réessayer"): st.rerun()
            else:
                st.warning("Ce n'est pas ça ! Un nouvel indice a peut-être été débloqué.")

    if st.button("Abandonner"):
        st.session_state.game_active = False
        st.rerun()