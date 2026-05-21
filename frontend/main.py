import streamlit as st
import requests
import os

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Logiciel de Vente Pro", layout="centered")

# Initialisation des états de session
if "auth" not in st.session_state:
    st.session_state["auth"] = False

# --- ÉCRAN DE CONNEXION ---
if not st.session_state["auth"]:
    st.title("🔐 Connexion")
    with st.container(border=True):
        user = st.text_input("Nom d'utilisateur")
        pw = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter", use_container_width=True):
            try:
                res = requests.post(f"{BACKEND_URL}/login", json={"username": user, "password": pw})
                if res.status_code == 200:
                    st.session_state["auth"] = True
                    st.rerun()
                else:
                    st.error("Identifiants invalides")
            except:
                st.error("Erreur: Le Backend est hors ligne")

# --- INTERFACE PRINCIPALE ---
else:
    # Barre latérale pour déconnexion
    with st.sidebar:
        st.title("Menu")
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state["auth"] = False
            st.rerun()

    st.title("📦 Gestion des Ventes")

    # 1. AJOUTER UNE VENTE
    with st.expander("➕ Ajouter une nouvelle vente", expanded=True):
        with st.form("form_ajout", clear_on_submit=True):
            nom = st.text_input("Nom du produit")
            prix = st.number_input("Prix (€)", min_value=0.0, step=0.01)
            if st.form_submit_button("Enregistrer la vente"):
                if nom:
                    requests.post(f"{BACKEND_URL}/ventes", json={"produit": nom, "prix": prix})
                    st.success(f"Vente de '{nom}' ajoutée avec succès !")
                    st.rerun()
                else:
                    st.warning("Veuillez entrer un nom de produit")

    # 2. HISTORIQUE ET ACTIONS
    st.subheader("📊 Historique des ventes")
    try:
        ventes = requests.get(f"{BACKEND_URL}/ventes").json()
        
        if not ventes:
            st.info("Aucune vente enregistrée.")
        else:
            for v in ventes:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.write(f"**{v['produit']}**")
                    c1.write(f"{v['prix']} €")
                    
                    # Bouton Modifier
                    if c2.button("✏️", key=f"edit_btn_{v['id']}"):
                        st.session_state[f"edit_mode_{v['id']}"] = True
                    
                    # Bouton Supprimer
                    if c3.button("🗑️", key=f"del_btn_{v['id']}"):
                        st.session_state[f"del_confirm_{v['id']}"] = True

                    # --- LOGIQUE DE SUPPRESSION (Confirmation) ---
                    if st.session_state.get(f"del_confirm_{v['id']}", False):
                        st.warning(f"Supprimer {v['produit']} ?")
                        col_y, col_n = st.columns(2)
                        if col_y.button("Oui", key=f"y_{v['id']}"):
                            requests.delete(f"{BACKEND_URL}/ventes/{v['id']}")
                            st.session_state[f"del_confirm_{v['id']}"] = False
                            st.rerun()
                        if col_n.button("Non", key=f"n_{v['id']}"):
                            st.session_state[f"del_confirm_{v['id']}"] = False
                            st.rerun()

                    # --- LOGIQUE DE MODIFICATION (Formulaire) ---
                    if st.session_state.get(f"edit_mode_{v['id']}", False):
                        with st.form(key=f"edit_form_{v['id']}"):
                            new_nom = st.text_input("Nouveau nom", value=v['produit'])
                            new_prix = st.number_input("Nouveau prix", value=float(v['prix']))
                            if st.form_submit_button("Confirmer la modification"):
                                requests.put(f"{BACKEND_URL}/ventes/{v['id']}", 
                                             json={"produit": new_nom, "prix": new_prix})
                                st.session_state[f"edit_mode_{v['id']}"] = False
                                st.rerun()
                            if st.button("Annuler"):
                                st.session_state[f"edit_mode_{v['id']}"] = False
                                st.rerun()

    except Exception as e:
        st.error("Impossible de charger les données.")