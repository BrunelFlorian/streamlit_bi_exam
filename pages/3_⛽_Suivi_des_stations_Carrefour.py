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
