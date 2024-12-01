import pandas as pd
import streamlit as st
from tools import load_styles, load_data

### Configuration de la page --------------------------------------------------------------------------------------------

# Titre de la page
st.set_page_config(page_title="Examen BI Florian Brunel", page_icon="📝", layout="wide")

# Chargement des styles CSS et chargement des icones Material
load_styles("725d3ddf")
load_data(radius=10)

# Titre du document
st.markdown(
    "<h1 style='text-align: center;'>Examen BI Florian Brunel 📝</h1><hr />",
    unsafe_allow_html=True,
)

### Contenu de la page --------------------------------------------------------------------------------------------------

# Contenu d'accueil
st.markdown(
    """
        <div class="w-full p-4 text-center bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700">
            <h5 class="mb-2 text-3xl font-bold text-gray-900 dark:text-white">Visualisation de données avec Streamlit</h5>
            <p class="mb-5 text-base text-gray-500 sm:text-lg dark:text-gray-400">Projet M2IA - Examen BI</p>
        </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
        ## 📚 Consignes de l'examen
        ### **Étape A : KPIs**
        Calculez le prix moyen (par jour sélectionné) pour chaque enseigne : Carrefour, Auchan,
E.Leclerc, Total Access, Intermarché et Système U
        ### **Étape B : Cartes**
        1. Affichage sur une carte avec Folium :
            - Pour chaque station Carrefour sélectionnée, affichez sur une carte la station Carrefour ainsi que les stations concurrentes dans un rayon de 10 km (en utilisant les données du fichier JSON).
            - Ajoutez un pop-up pour chaque station avec le nom de l’enseigne et la ville.
        2. Tableau de comparaison des prix :
            - Pour chaque type de carburant, affichez dans un tableau les prix de la station Carrefour sélectionnée ainsi que ceux de ses concurrents, triés par ordre décroissant.
            - Affichez la ligne Carrefour en vert pour une meilleure lisibilité.
        3. Courbes de prix :
            - Permettez à l’utilisateur de sélectionner une plage de dates (début et fin).
            - Pour chaque type de carburant, affichez une courbe montrant l’évolution des prix pour la station Carrefour sélectionnée ainsi que celle de ses concurrents dans un rayon de 10 km.
        4. Déploiement de l’application :
            Déployez l’application avec Streamlit et GitHub.
    """
)
