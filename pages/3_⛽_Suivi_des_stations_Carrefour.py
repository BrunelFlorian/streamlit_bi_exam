import json
import folium
import pandas as pd
import streamlit as st
from tools import load_styles, load_data  # Importation de load_data depuis tools
from streamlit_folium import folium_static

# Configuration Streamlit
st.set_page_config(
    page_title="Suivi des stations Carrefour", page_icon="⛽", layout="wide"
)
load_styles("d135bf9")
st.markdown(
    "<h1 style='text-align: center;'>Suivi des stations Carrefour ⛽</h1><hr />",
    unsafe_allow_html=True,
)

### Charger les données -----------------------------------------------------------------
# Slider pour définir le rayon de recherche
search_radius_km = st.slider(
    "Sélectionnez le rayon de recherche (km) :", min_value=1, max_value=50, value=10
)

# Charger les données en utilisant load_data
load_data(radius=search_radius_km)

# Charger les données des stations Carrefour et des concurrents
carrefour_stations = pd.read_csv("./data/Carrefour.csv")
concurrent_stations = pd.read_csv("./data/Concurrents.csv")
prices = pd.read_csv("./data/prix.csv")

# Correction des coordonnées
carrefour_stations["Latitude"] /= 10**5
carrefour_stations["Longitude"] /= 10**5
concurrent_stations["Latitude"] /= 10**5
concurrent_stations["Longitude"] /= 10**5

# Charger la liste des concurrents pour le rayon défini
with open(f"./data/concurrents_{search_radius_km}km.json", "r") as f:
    concurrents_km = json.load(f)

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

### Carte avec les stations et concurrents ---------------------------------------------
# Créer une carte centrée sur la station sélectionnée
map_france = folium.Map(
    location=[selected_station["Latitude"], selected_station["Longitude"]],
    zoom_start=10,
)

# Ajouter un cercle représentant le rayon de recherche des concurrents
search_radius_m = search_radius_km * 1000  # Convertir en mètres

popup_radius_html = f"""
    <div style="font-size: 14px; color: black; background-color: #f9f9f9; padding: 10px; border-radius: 8px; width: 200px; max-width: 100%;">
        Rayon de recherche : <b>{search_radius_km} km</b>
    </div>
"""

folium.Circle(
    location=[selected_station["Latitude"], selected_station["Longitude"]],
    radius=search_radius_m,
    color="blue",
    fill=True,
    fill_opacity=0.1,
    popup=popup_radius_html,
).add_to(map_france)

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
    icon=folium.features.CustomIcon("./images/carrefour.png", icon_size=(40, 30)),
).add_to(map_france)

# Ajouter les concurrents trouvés à la carte
for concurrent_id in concurrents_km.get(str(selected_station_id), []):
    concurrent = concurrent_dict.get(str(concurrent_id), None)
    if concurrent and "Carrefour" not in concurrent["Enseignes"]:  # Exclure Carrefour
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

# Afficher la carte dans Streamlit
folium_static(map_france)

### Comparaison des prix ---------------------------------------------------------------

# Fusionner les données des prix avec les informations des stations
stations_info = pd.concat([carrefour_stations, concurrent_stations], ignore_index=True)
stations_info = stations_info.rename(columns={"ID": "id"})

# Identifier les colonnes de produits dans le DataFrame des prix
product_columns = (
    prices.select_dtypes(include=["float", "int"]).columns.difference(["id"]).tolist()
)  # Exclure l'ID si présent
product_columns.insert(0, "Tous")  # Ajouter l'option "Tous" en premier

# Sélectionner dynamiquement un produit
selected_product = st.sidebar.selectbox(
    "Choisissez le produit à analyser :", product_columns
)

# Jointure pour ajouter les informations (Ville et Enseignes) aux prix
prices = prices.merge(stations_info[["id", "Ville", "Enseignes"]], on="id", how="left")

# Filtrer les prix pour la station Carrefour sélectionnée et ses concurrents
selected_station_prices = prices[prices["id"] == selected_station_id]
concurrent_prices = prices[
    prices["id"].isin(map(int, concurrents_km.get(str(selected_station_id), [])))
]

# Concaténer les données
comparison_df = pd.concat([selected_station_prices, concurrent_prices])


# Filtrer les lignes avec des valeurs de produit non nulles
def filter_non_zero(df, product, carrefour_id):
    """Exclut les lignes où le produit est 0, sauf pour la station Carrefour sélectionnée."""
    return df[(df[product] != 0) | (df["id"] == carrefour_id)]


# Mise en évidence de la station Carrefour en vert
def highlight_carrefour(row):
    if selected_station["Enseignes"] in row.values:  # Compare par "Enseignes"
        return ["background-color: lightgreen"] * len(row)
    return [""] * len(row)


# Si "Tous" est sélectionné, générer un tableau pour chaque produit
if selected_product == "Tous":
    st.markdown(
        f"<hr /><h1 class='subtitle' style='text-align: center;'>Comparaison prix moyens pour tous les produits</h1><hr />",
        unsafe_allow_html=True,
    )

    unavailable_products = []  # Produits non vendus
    available_products = []  # Produits vendus

    # Filtrer les produits
    all_products = prices.select_dtypes(include=["float", "int"]).columns.difference(
        ["id"]
    )
    for product in all_products:
        carrefour_product_price = (
            selected_station_prices[product].values[0]
            if not selected_station_prices.empty
            else 0
        )
        if carrefour_product_price == 0:
            unavailable_products.append(product)
        else:
            available_products.append(product)

    # Grouper les tableaux par tranches de trois produits
    for i in range(0, len(available_products), 3):
        current_products = available_products[i : i + 3]
        columns = st.columns(len(current_products))  # Créez les colonnes dynamiquement

        for col, product in zip(columns, current_products):
            # Calculer les données pour le tableau
            comparison_avg_df = (
                comparison_df.groupby(["id", "Enseignes", "Ville"], as_index=False)
                .agg({product: "mean"})
                .sort_values(by=product, ascending=True)
            )
            comparison_avg_df = filter_non_zero(
                comparison_avg_df, product, selected_station_id
            )
            if selected_station_id not in comparison_avg_df["id"].values:
                continue
            df_to_display = comparison_avg_df.drop(columns=["id"], errors="ignore")

            # Afficher le tableau dans la colonne
            with col:
                st.markdown(
                    f"<h3 class='subtitle' style='text-align: center;'>{product}</h3>",
                    unsafe_allow_html=True,
                )
                st.dataframe(
                    df_to_display.style.apply(highlight_carrefour, axis=1),
                    height=200,
                    hide_index=True,
                    use_container_width=True,
                )

    # Afficher les produits non vendus
    if unavailable_products:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning(
            "### ⚠️ Produits non vendus par la station sélectionnée : "
            + ", ".join(unavailable_products)
        )
    else:
        st.info("### La station sélectionnée vend tous les produits.")
else:
    # Vérifiez si le prix du produit est 0 pour la station Carrefour sélectionnée
    carrefour_product_price = (
        selected_station_prices[selected_product].values[0]
        if not selected_station_prices.empty
        else 0
    )

    if carrefour_product_price == 0:
        # Affichez un message indiquant que la station ne vend pas ce produit
        st.write(
            f"### La station Carrefour **{selected_station['Enseignes']} ({selected_station['Ville']})** ne vend pas le produit sélectionné : **{selected_product}**."
        )
    else:
        # Calcul de la moyenne pour le produit sélectionné
        comparison_avg_df = (
            comparison_df.groupby(["id", "Enseignes", "Ville"], as_index=False)
            .agg({selected_product: "mean"})
            .sort_values(by=selected_product, ascending=True)
        )

        # Filtrer les lignes où la valeur du produit est 0, sauf pour la station Carrefour
        comparison_avg_df = filter_non_zero(
            comparison_avg_df, selected_product, selected_station_id
        )

        # Vérification si la station Carrefour est présente
        if selected_station_id not in comparison_avg_df["id"].values:
            st.warning(
                f"⚠️ La station Carrefour n'a pas de données valides pour le produit {selected_product}."
            )
        else:
            # Supprimer les colonnes ID avant d'afficher
            df_to_display = comparison_avg_df.drop(columns=["id"], errors="ignore")

            # Afficher le tableau pour le produit sélectionné
            st.markdown(
                f"<hr /><h1 class='subtitle' style='text-align: center;'>Comparaison des prix moyens pour le {selected_product}</h1><hr />",
                unsafe_allow_html=True,
            )
            st.dataframe(
                df_to_display.style.apply(highlight_carrefour, axis=1),
                hide_index=True,
                use_container_width=True,
            )

### Afficher les courbes de prix ----------------------------------------------------------------------------------------
import itertools

# Générer des couleurs uniques pour les enseignes
color_palette = itertools.cycle(
    [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]
)
unique_colors = {
    enseigne: next(color_palette) for enseigne in prices["Enseignes"].unique()
}

import plotly.express as px  # Pour tracer des graphiques interactifs
import plotly.graph_objects as go  # Pour combiner plusieurs courbes

st.markdown(
    f"<hr /><h1 class='subtitle' style='text-align: center;'>Courbes d'évolution des prix</h1><hr />",
    unsafe_allow_html=True,
)

# Conversion de la colonne 'Date' en datetime
prices["Date"] = pd.to_datetime(prices["Date"], errors="coerce")

# Définir les plages minimales et maximales des dates à partir des données
min_date = pd.to_datetime(prices["Date"].min())
max_date = pd.to_datetime(prices["Date"].max())

# Ajout du sélecteur de plage de dates dans la barre latérale avec bornes
start_date = st.sidebar.date_input(
    "Date de début", value=min_date, min_value=min_date, max_value=max_date
)
end_date = st.sidebar.date_input(
    "Date de fin", value=max_date, min_value=min_date, max_value=max_date
)

# Filtrer les données de prix pour la plage de dates sélectionnée
filtered_prices = prices[
    (prices["Date"] >= pd.to_datetime(start_date))
    & (prices["Date"] <= pd.to_datetime(end_date))
]

# Vérifier si des données sont disponibles pour la plage de dates
if filtered_prices.empty:
    st.warning(
        "⚠️ Aucune donnée de prix disponible pour la plage de dates sélectionnée."
    )
else:
    # Vérifiez si un produit spécifique ou "Tous" est sélectionné
    if selected_product == "Tous":
        # Parcourir tous les produits disponibles
        for product in prices.select_dtypes(
            include=["float", "int"]
        ).columns.difference(["id"]):
            carrefour_prices = filtered_prices[
                filtered_prices["id"] == selected_station_id
            ]
            competitors_prices = filtered_prices[
                filtered_prices["id"].isin(
                    map(int, concurrents_km.get(str(selected_station_id), []))
                )
            ]

            # Créer un graphique pour ce produit, même avec données partielles
            fig = go.Figure()

            # Ajouter la courbe Carrefour, vérifier si des données existent
            if (
                not carrefour_prices.empty
                and (carrefour_prices[selected_product] != 0).any()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=carrefour_prices["Date"],
                        y=carrefour_prices[selected_product],
                        mode="lines",
                        name="Carrefour",
                        line=dict(color=unique_colors.get("Carrefour", "lightgreen")),
                        opacity=1,
                    )
                )
            else:
                st.warning(f"⚠️ Carrefour ne vend pas le produit : {product}.")

            # Ajouter des courbes pour les concurrents avec une opacité ajustée
            for competitor_id in concurrents_km.get(str(selected_station_id), []):
                competitor_prices = competitors_prices[
                    competitors_prices["id"] == int(competitor_id)
                ]
                if (
                    not competitor_prices.empty
                    and (competitor_prices[selected_product] != 0).any()
                ):
                    competitor_name = concurrent_dict.get(str(competitor_id), {}).get(
                        "Enseignes", f"Concurrent {competitor_id}"
                    )
                    competitor_color = unique_colors.get(
                        competitor_name, "#7f7f7f"
                    )  # Couleur par défaut si non définie
                    fig.add_trace(
                        go.Scatter(
                            x=competitor_prices["Date"],
                            y=competitor_prices[selected_product],
                            mode="lines",
                            name=f"{competitor_name}",
                            line=dict(color=competitor_color, dash="dot"),
                            opacity=0.7,
                        )
                    )

            # Vérifier si le graphique contient des courbes
            if len(fig.data) > 0:
                # Personnaliser le style du graphique
                fig.update_layout(
                    title=f"Évolution des prix - {product}",
                    xaxis_title="Date",
                    yaxis_title="Prix (€)",
                    title_x=0.5,
                    template="plotly_white",
                )

                # Afficher le graphique dans Streamlit
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"Aucune donnée disponible pour le produit : {product}.")
    else:
        # Si un produit spécifique est sélectionné
        carrefour_prices = filtered_prices[filtered_prices["id"] == selected_station_id]
        competitors_prices = filtered_prices[
            filtered_prices["id"].isin(
                map(int, concurrents_km.get(str(selected_station_id), []))
            )
        ]

        # Créer un graphique pour le produit sélectionné
        fig = go.Figure()

        # Ajouter la courbe pour Carrefour
        if (
            not carrefour_prices.empty
            and (carrefour_prices[selected_product] != 0).any()
        ):
            fig.add_trace(
                go.Scatter(
                    x=carrefour_prices["Date"],
                    y=carrefour_prices[selected_product],
                    mode="lines",
                    name="Carrefour",
                    line=dict(color="lightgreen"),
                    opacity=1,  # Opacité maximale pour Carrefour
                )
            )
        else:
            st.warning(f"⚠️ Carrefour ne vend pas le produit : {selected_product}.")

        # Ajouter des courbes pour les concurrents avec une opacité ajustée
        for competitor_id in concurrents_km.get(str(selected_station_id), []):
            competitor_prices = competitors_prices[
                competitors_prices["id"] == int(competitor_id)
            ]
            if (
                not competitor_prices.empty
                and (competitor_prices[selected_product] != 0).any()
            ):
                competitor_name = concurrent_dict.get(str(competitor_id), {}).get(
                    "Enseignes", f"Concurrent {competitor_id}"
                )
                competitor_color = unique_colors.get(
                    competitor_name, "#7f7f7f"
                )  # Couleur par défaut si non définie
                fig.add_trace(
                    go.Scatter(
                        x=competitor_prices["Date"],
                        y=competitor_prices[selected_product],
                        mode="lines",
                        name=f"{competitor_name}",
                        line=dict(color=competitor_color, dash="dot"),
                        opacity=0.7,
                    )
                )

        # Vérifier si le graphique contient des courbes
        if len(fig.data) > 0:
            fig.update_layout(
                title=f"Évolution des prix - {selected_product}",
                xaxis_title="Date",
                yaxis_title="Prix (€)",
                title_x=0.5,
                template="plotly_white",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(
                f"⚠️ Aucune donnée disponible pour le produit : {selected_product}."
            )
