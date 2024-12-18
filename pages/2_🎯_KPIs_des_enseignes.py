import pandas as pd
import streamlit as st
from tools import load_styles

# Configuration de la page
st.set_page_config(page_title="KPIs des enseignes", page_icon="🎯", layout="wide")
load_styles("d813c640")
st.markdown(
    "<h1 style='text-align: center;'>KPIs des enseignes 🎯</h1><hr />",
    unsafe_allow_html=True,
)

# Chargement des données
stations = pd.read_csv("./data/stations.csv")
prix = pd.read_csv("./data/prix.csv", dtype={"Date": str})

# Dictionnaire des variations d'enseignes
enseigne_mapping = {
    "Système U": [
        "système u",
        "super u",
        "systeme u",
        "systï¿½me u",
        "u express",
        "station u",
    ],
    "Intermarché": [
        "intermarché",
        "intermarche",
        "intermarchï¿½",
        "intermarché contact",
    ],
    "E.Leclerc": ["e.leclerc", "leclerc"],
    "Carrefour": [
        "carrefour",
        "carrefour market",
        "carrefour contact",
        "carrefour express",
        "crf contact",
    ],
    "Total Access": ["totalenergies access"],
    "Auchan": ["auchan"],
}

# Création du dictionnaire inversé
variation_to_enseigne = {
    variation: enseigne
    for enseigne, variations in enseigne_mapping.items()
    for variation in variations
}


# Fonction de détection des enseignes optimisée
def detect_enseigne(text):
    if pd.isna(text):
        return None
    text_lower = text.lower()
    for variation, enseigne in variation_to_enseigne.items():
        if variation in text_lower:
            return enseigne
    return None


# Appliquer la détection optimisée
stations["Enseigne_detectée"] = stations["Enseignes"].apply(detect_enseigne)

# Grouper les IDs par enseigne détectée
ids_par_enseigne = stations.groupby("Enseigne_detectée")["ID"].apply(list).to_dict()

# Préparation des données de prix
prix["Date"] = pd.to_datetime(prix["Date"], format="%Y-%m-%d")

# Identifier les carburants non vendus par station (prix toujours à 0)
carburants = ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]
for carburant in carburants:
    prix.loc[prix.groupby("id")[carburant].transform("sum") == 0, carburant] = (
        None  # Marquer comme non vendu
    )

# Propager les valeurs manquantes pour gérer les ruptures
prix.ffill(inplace=True)

# Sélectionner une date avec la sidebar
selected_date = st.sidebar.date_input(
    "Sélectionnez une date",
    value=prix["Date"].max(),
    min_value=prix["Date"].min(),
    max_value=prix["Date"].max(),
    format="DD/MM/YYYY",
)

selected_date = pd.to_datetime(selected_date)
filtered_price = prix[prix["Date"] == selected_date]

# Calculer les prix moyens par enseigne
kpis = {
    enseigne: filtered_price[filtered_price["id"].isin(ids)][carburants].mean()
    for enseigne, ids in ids_par_enseigne.items()
}

# Identifier les prix minimums et maximums pour chaque carburant
carburant_mins = {carburant: None for carburant in carburants}
carburant_maxs = {carburant: None for carburant in carburants}

for carburant in carburants:
    prix_moyens_par_enseigne = {
        enseigne: moyenne[carburant]
        for enseigne, moyenne in kpis.items()
        if not pd.isna(moyenne[carburant])
    }
    if prix_moyens_par_enseigne:
        carburant_mins[carburant] = min(prix_moyens_par_enseigne.values())
        carburant_maxs[carburant] = max(prix_moyens_par_enseigne.values())

# Affichage des résultats avec le style Tailwind et disposition en colonnes
enseigne_list = list(kpis.items())
n = len(enseigne_list)

for i in range(0, n, 3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        if i + j < n:
            enseigne, moyenne = enseigne_list[i + j]
            items_html = ""
            for carburant, prix_moyen in moyenne.items():
                if pd.isna(prix_moyen):
                    continue
                # Appliquer des styles conditionnels
                if prix_moyen == carburant_mins[carburant]:
                    style = "color: green; font-weight: bold;"
                elif prix_moyen == carburant_maxs[carburant]:
                    style = "color: red; font-weight: bold;"
                else:
                    style = ""
                items_html += f"""
                    <li class="py-3 sm:py-4">
                        <div class="flex items-center">
                            <div class="flex-1 min-w-0 ms-4">
                                <p class="text-sm font-medium text-gray-900 truncate dark:text-white">{carburant}</p>
                            </div>
                            <div class="inline-flex items-center text-base font-semibold text-gray-900 dark:text-white" style="{style}">
                                {prix_moyen:.3f} €
                            </div>
                        </div>
                    </li>
                """
            col.markdown(
                f"""
                    <div class="w-full max-w-md p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700">
                        <div class="flex items-center justify-between mb-4">
                            <h5 class="text-xl font-bold leading-none text-gray-900 dark:text-white">{enseigne}</h5>
                        </div>
                        <div class="flow-root">
                            <ul role="list" class="divide-y divide-gray-200 dark:divide-gray-700">
                                {items_html}
                    </div>
                """,
                unsafe_allow_html=True,
            )

# Informations supplémentaires
st.info(
    "Les prix affichés en vert sont les prix moyens les plus bas et les prix affichés en rouge sont les prix moyens les plus élevés."
)
