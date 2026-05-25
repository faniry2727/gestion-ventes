import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
st.set_page_config(page_title="SalesManager Pro", layout="wide", page_icon="📈")

# --- STYLE CSS (Visibilité améliorée) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-left: 5px solid #4F8BF9;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    [data-testid="stMetricLabel"] > div { color: #555555 !important; font-weight: bold; }
    [data-testid="stMetricValue"] > div { color: #111111 !important; }
    </style>
    """, unsafe_allow_html=True)

if "auth" not in st.session_state: st.session_state["auth"] = False

# --- DIALOGUES DE CONFIRMATION ---
@st.dialog("📝 Modifier la transaction")
def edit_dialog(vente):
    nom = st.text_input("Produit", value=vente['produit'])
    c1, c2 = st.columns(2)
    qty = c1.number_input("Quantité", value=int(vente['quantite']), min_value=1)
    pu = c2.number_input("Prix Unitaire (€)", value=float(vente['prix_unitaire']), min_value=0.0)
    st.write(f"**Nouveau total : {qty * pu:,.2f} €**")
    if st.button("Enregistrer les modifications", use_container_width=True):
        requests.put(f"{BACKEND_URL}/ventes/{vente['id']}", 
                     json={"produit": nom, "quantite": qty, "prix_unitaire": pu})
        st.rerun()

@st.dialog("⚠️ Supprimer cette vente")
def delete_dialog(vente):
    st.error(f"Supprimer définitivement **{vente['produit']}** ?")
    if st.button("Confirmer la suppression", use_container_width=True):
        requests.delete(f"{BACKEND_URL}/ventes/{vente['id']}")
        st.rerun()

# --- LOGIN (Inchangé) ---
if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.write("#")
        st.markdown("<h1 style='text-align: center;'>Connexion</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            user = st.text_input("Utilisateur")
            pw = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter", use_container_width=True):
                try:
                    res = requests.post(f"{BACKEND_URL}/login", json={"username": user, "password": pw})
                    if res.status_code == 200:
                        st.session_state["auth"] = True
                        st.rerun()
                    else: st.error("Erreur d'accès")
                except: st.error("Serveur injoignable")

# --- INTERFACE PRINCIPALE ---
else:
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3258/3258446.png", width=80)
        st.title("SalesManager")
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state["auth"] = False
            st.rerun()

    st.title("Dashboard Commercial")
    
    # Calcul des stats
    try:
        ventes = requests.get(f"{BACKEND_URL}/ventes").json()
        total_ca = sum(v['quantite'] * v['prix_unitaire'] for v in ventes)
        total_articles = sum(v['quantite'] for v in ventes)
        nb_transac = len(ventes)
    except:
        total_ca, total_articles, nb_transac, ventes = 0, 0, 0, []

    # Mise à jour des rectangles blancs
    k1, k2, k3 = st.columns(3)
    k1.metric("Chiffre d'Affaires Total", f"{total_ca:,.2f} €")
    k2.metric("Articles Vendus", total_articles)
    k3.metric("Nombre de Transactions", nb_transac)

    st.write("---")

    # Formulaire d'ajout
    with st.expander("➕ Enregistrer une nouvelle transaction"):
        with st.form("new_sale", clear_on_submit=True):
            f1, f2, f3 = st.columns([2, 1, 1])
            p_nom = f1.text_input("Désignation du produit")
            p_qty = f2.number_input("Quantité", min_value=1, step=1)
            p_pu = f3.number_input("Prix Unitaire (€)", min_value=0.0, step=0.01)
            if st.form_submit_button("Enregistrer la vente", use_container_width=True):
                if p_nom:
                    requests.post(f"{BACKEND_URL}/ventes", 
                                  json={"produit": p_nom, "quantite": p_qty, "prix_unitaire": p_pu})
                    st.rerun()

    # Historique
    st.subheader("Historique des transactions")
    if not ventes:
        st.info("Aucune transaction.")
    else:
        # En-têtes
        h = st.columns([1, 3, 1, 2, 2, 2])
        h[0].write("**ID**")
        h[1].write("**Produit**")
        h[2].write("**Qté**")
        h[3].write("**P.U.**")
        h[4].write("**Total**")
        h[5].write("**Actions**")

        for v in ventes:
            with st.container(border=True):
                c = st.columns([1, 3, 1, 2, 2, 2])
                c[0].write(f"#{v['id']}")
                c[1].write(f"**{v['produit']}**")
                c[2].write(str(v['quantite']))
                c[3].write(f"{v['prix_unitaire']} €")
                # Calcul automatique du total de la ligne
                total_ligne = v['quantite'] * v['prix_unitaire']
                c[4].write(f"**{total_ligne:,.2f} €**")
                
                b1, b2 = c[5].columns(2)
                if b1.button("✏️", key=f"e_{v['id']}"): edit_dialog(v)
                if b2.button("🗑️", key=f"d_{v['id']}"): delete_dialog(v)