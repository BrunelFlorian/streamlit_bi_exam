import json
import folium
import pandas as pd
import streamlit as st
from tools import load_styles
from streamlit_folium import folium_static

# Configuration Streamlit
st.set_page_config(page_title="Suivi des stations Carrefour", page_icon="⛽")
load_styles("d135bf9")
st.markdown(
    "<h1 style='text-align: center;'>Suivi des stations Carrefour ⛽</h1><hr />",
    unsafe_allow_html=True,
)

### Afficher la carte des stations Carrefour et de leurs concurrents ----------------------------------------------------

# Charger les données
carrefour_stations = pd.read_csv("exam_florian_brunel/Carrefour.csv")
concurrent_stations = pd.read_csv("exam_florian_brunel/Concurrents.csv")

# Charger le fichier JSON des concurrents
with open("exam_florian_brunel/concurrents_10km.json", "r") as f:
    concurrents_10km = json.load(f)

# Correction des coordonnées
carrefour_stations["Latitude"] /= 10**5
carrefour_stations["Longitude"] /= 10**5
concurrent_stations["Latitude"] /= 10**5
concurrent_stations["Longitude"] /= 10**5

# Préparer un dictionnaire pour un accès rapide aux concurrents
concurrent_dict = concurrent_stations.set_index("ID").to_dict(orient="index")
concurrent_dict = {str(key): value for key, value in concurrent_dict.items()}

# Liste déroulante pour sélectionner une station Carrefour
station_options = carrefour_stations.set_index("ID").to_dict(orient="index")
selected_station_id = st.sidebar.selectbox(
    "Choisissez une station Carrefour :",
    options=station_options.keys(),
    format_func=lambda x: f"{station_options[x]['Enseignes']} ({station_options[x]['Ville']})",
)

# Obtenir les informations de la station sélectionnée
selected_station = station_options[selected_station_id]

# Créer une carte centrée sur la station sélectionnée
map_france = folium.Map(
    location=[selected_station["Latitude"], selected_station["Longitude"]],
    zoom_start=11.5,
)

# Ajouter un marqueur pour la station Carrefour sélectionnée
popup_selected_html = f"""
    <div style="font-size: 14px; color: black; background-color: #f9f9f9; padding: 10px; border-radius: 8px; width: 200px; max-width: 100%;">
        <b>{selected_station['Enseignes']}</b><br>
        Ville : {selected_station['Ville']}
    </div>
"""

folium.Marker(
    location=[selected_station["Latitude"], selected_station["Longitude"]],
    popup=folium.Popup(popup_selected_html),
    icon=folium.Icon(color="blue", icon="info-sign"),
    min_width=300,
).add_to(map_france)

# Afficher les concurrents pour la station sélectionnée
if str(selected_station_id) in concurrents_10km:
    concurrents_ids = concurrents_10km[str(selected_station_id)]
    for concurrent_id in concurrents_ids:
        if concurrent_id in concurrent_dict:
            concurrent = concurrent_dict[concurrent_id]
            # Vérification : exclure les stations Carrefour
            if "Carrefour" not in concurrent["Enseignes"]:
                popup_html = f"""
                    <div style="font-size: 14px; color: black; background-color: #f9f9f9; padding: 10px; border-radius: 8px; width: 150px; max-width: 100%;">
                        <b>{concurrent['Enseignes']}</b><br>
                        Ville : {concurrent['Ville']}
                    </div>
                """
                folium.Marker(
                    location=[concurrent["Latitude"], concurrent["Longitude"]],
                    popup=folium.Popup(popup_html),
                    icon=folium.Icon(color="red", icon="info-sign"),
                ).add_to(map_france)
            else:
                st.write(f"Exclu (Carrefour) : {concurrent}")
else:
    st.write("Aucun concurrent trouvé dans un rayon de 10 km pour cette station.")

# Afficher la carte dans Streamlit
folium_static(map_france)

### Afficher les informations détaillées de la station Carrefour sélectionnée -----------------------------------------
# Exemples de données de carburant
carrefour_station_prices = {
    "station": "Carrefour Market (SAINT-DENIS-LèS-BOURG)",
    "prix_gazole": 1.35,
    "prix_essence": 1.45,
    "prix_e85": 0.90,
}

# Exemple de données pour les concurrents
concurrents_prices = [
    {
        "station": "Concurent 1",
        "prix_gazole": 1.40,
        "prix_essence": 1.47,
        "prix_e85": 0.93,
    },
    {
        "station": "Concurent 2",
        "prix_gazole": 1.33,
        "prix_essence": 1.50,
        "prix_e85": 0.88,
    },
    {
        "station": "Concurent 3",
        "prix_gazole": 1.32,
        "prix_essence": 1.43,
        "prix_e85": 0.85,
    },
]

# Créer un DataFrame pour les concurrents
concurrents_df = pd.DataFrame(concurrents_prices)

# Ajouter la ligne Carrefour à ce DataFrame
carrefour_df = pd.DataFrame([carrefour_station_prices])
carrefour_df["station"] = carrefour_station_prices[
    "station"
]  # Assurez-vous que le nom est défini
full_df = pd.concat([concurrents_df, carrefour_df], ignore_index=True)


# Fonction pour afficher le tableau trié par chaque carburant
def display_comparison_table(df, fuel_type):
    # Trier par type de carburant spécifique
    df_sorted = df.sort_values(by=f"prix_{fuel_type}", ascending=False)

    # Mettre en évidence la ligne Carrefour en vert
    def highlight_row(s):
        return [
            (
                "background-color: green"
                if v == carrefour_station_prices["station"]
                else ""
            )
            for v in s
        ]

    # Afficher le tableau
    st.write(f"**Comparaison des prix pour le carburant {fuel_type.capitalize()}**")
    st.dataframe(df_sorted.style.apply(highlight_row, subset=["station"], axis=1))


# Afficher les tableaux pour chaque carburant
for fuel_type in ["gazole", "essence", "e85"]:
    display_comparison_table(full_df, fuel_type)
