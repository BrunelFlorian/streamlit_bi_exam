import math
import json
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html


def load_styles(anchor_name: str):
    # Chargement des styles CSS
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Chargement des icones Material et de Tailwind
    st.markdown(
        """
            <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet" />
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        """,
        unsafe_allow_html=True,
    )

    ## Configuration de la barre latérale
    st.sidebar.markdown(
        """
        <h2 style='text-align: center;'>Master 2 IA - 28/11/2024</h2>
        <div class="logo" style="text-align: center;">
            <img src="https://my.ecole-hexagone.com/logo-small.svg" width="100">
        </div>
        <h2 style='text-align: center;'>Florian Brunel</h2>
        <hr />
        """,
        unsafe_allow_html=True,
    )

    # Bouton pour remonter en haut de la page
    st.markdown(
        """
        <a class="scroll-to-top" target="_self" href="#"""
        + anchor_name
        + """">
            <span class="material-icons">keyboard_arrow_up</span>
        </a>
        """,
        unsafe_allow_html=True,
    )

    # Ajouter le footer
    st.markdown(
        """
            <div class="footer">
                <p>Copyright © - 2024 - Florian Brunel<p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # Injecter du JavaScript pour récupérer la largeur de la sidebar et adapter le footer
    html(
        """
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    // Accéder à la sidebar et au footer dans le DOM parent
                    var sidebar = window.parent.document.querySelector('.stSidebar');
                    var footer = window.parent.document.querySelector('.footer');
                    
                    if (sidebar && footer) {
                        console.log("Sidebar et footer trouvés dans le DOM parent.");
                        
                        // Fonction pour mettre à jour la largeur du footer
                        function updateFooterWidth() {
                            var screenWidth = window.parent.innerWidth; // Largeur de l'écran
                            var sidebarWidth = sidebar.offsetWidth; // Largeur de la sidebar
                            var footerWidth = screenWidth - sidebarWidth; // Calcul de la largeur du footer
                            
                            // Appliquer la largeur calculée au footer
                            footer.style.width = footerWidth + 'px';
                            footer.style.marginLeft = sidebarWidth + 'px'; // Ajuster la position pour éviter un chevauchement
                            console.log("Footer ajusté : largeur =", footerWidth, "px");
                        }

                        // Ajuster la largeur initialement
                        updateFooterWidth();

                        // Observer les changements de taille de la sidebar
                        var resizeObserver = new ResizeObserver(function() {
                            updateFooterWidth(); // Recalculer la largeur chaque fois que la sidebar change
                        });
                        resizeObserver.observe(sidebar);

                        // Ajouter un écouteur pour les changements de taille de la fenêtre
                        window.parent.addEventListener('resize', updateFooterWidth);
                    } else {
                        if (!sidebar) console.log("Sidebar non trouvée dans le DOM parent.");
                        if (!footer) console.log("Footer non trouvé dans le DOM parent.");
                    }
                });
            </script>
        """,
        height=0,
    )

    # Injecter du JavaScript pour afficher/masquer le bouton "Scroll to Top" en fonction du défilement
    html(
        """
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                // Accéder au bouton "Scroll to Top" dans le DOM parent
                var scrollButton = window.parent.document.querySelector('.scroll-to-top');

                if (scrollButton) {
                    console.log("Bouton 'Scroll to Top' trouvé.");

                    // Cacher le bouton initialement
                    scrollButton.style.opacity = 0;  // Initialement invisible
                    scrollButton.style.transition = 'opacity 0.3s ease, transform 0.3s ease'; // Transition pour animation
                    scrollButton.style.transform = 'translateY(10px)';  // Initialement légèrement décalé vers le bas

                    // Trouver le conteneur défilable principal (Streamlit)
                    var scrollContainer = window.parent.document.querySelector('.stMain');

                    if (scrollContainer) {
                        console.log("Conteneur défilable principal trouvé.");

                        // Fonction pour afficher/masquer le bouton
                        function toggleScrollButton() {
                            var scrollPosition = scrollContainer.scrollTop;
                            if (scrollPosition > 300) {
                                // Afficher le bouton avec animation
                                scrollButton.style.display = 'flex';  // Le bouton reste visible
                                setTimeout(function() {
                                    scrollButton.style.opacity = 1;  // Opacité à 1 pour rendre visible
                                    scrollButton.style.transform = 'translateY(0)';  // Retour à la position normale
                                }, 10);  // Attendre un peu avant d'ajouter l'animation
                            } else {
                                // Cacher le bouton avec animation uniquement après un certain délai
                                scrollButton.style.opacity = 0;  // Opacité à 0 pour rendre invisible
                                scrollButton.style.transform = 'translateY(10px)';  // Légèrement décalé vers le bas
                                
                                // Détecter la fin de la transition avant de masquer
                                setTimeout(function() {
                                    if (scrollContainer.scrollTop <= 100) {
                                        scrollButton.style.display = 'none';  // Masquer après l'animation
                                    }
                                }, 300);  // Délai pour attendre la fin de l'animation (300ms)
                            }
                        }

                        // Ajouter un gestionnaire d'événements pour le défilement sur le conteneur principal
                        scrollContainer.addEventListener('scroll', toggleScrollButton);

                        // Vérifier la position initiale
                        toggleScrollButton();
                    } else {
                        console.log("Conteneur défilable principal non trouvé.");
                    }
                } else {
                    console.log("Bouton 'Scroll to Top' non trouvé dans le DOM parent.");
                }
            });
        </script>
        """,
        height=0,
    )


@st.cache_data
def load_data(radius: int):
    # Charger le fichier infos_stations.csv
    infos_stations = pd.read_csv("exam_florian_brunel/data/stations.csv")

    # Filtrer les stations Carrefour
    carrefour_stations = infos_stations[
        infos_stations["Enseignes"].str.contains("Carrefour|CRF", na=False, case=False)
    ]
    concurrent_stations = infos_stations[
        ~infos_stations["Enseignes"].str.contains("Carrefour|CRF", na=False, case=False)
    ]

    # Sauvegarder les fichiers filtrés
    carrefour_stations.to_csv("exam_florian_brunel/data/Carrefour.csv", index=False)
    concurrent_stations.to_csv("exam_florian_brunel/data/Concurrents.csv", index=False)

    def haversine(lat1, lon1, lat2, lon2):
        # Convertir les degrés en radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        # Rayon moyen de la Terre en kilomètres
        R = 6371.0
        # Différences de coordonnées
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        # Formule de Haversine
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        # Distance en kilomètres
        distance = R * c
        return distance

    # Formater les latitudes et longitudes
    concurrent_stations["ID"] = concurrent_stations["ID"].apply(str)
    concurrent_stations["Latitude"] = (
        concurrent_stations["Latitude"].apply(float) / 100000
    )
    concurrent_stations["Longitude"] = (
        concurrent_stations["Longitude"].apply(float) / 100000
    )
    D1 = {
        concurrent_stations.loc[id, "ID"]: (
            concurrent_stations.loc[id, "Latitude"],
            concurrent_stations.loc[id, "Longitude"],
        )
        for id in concurrent_stations.index
    }

    carrefour_stations["ID"] = carrefour_stations["ID"].apply(str)
    carrefour_stations["Latitude"] = (
        carrefour_stations["Latitude"].apply(float) / 100000
    )
    carrefour_stations["Longitude"] = (
        carrefour_stations["Longitude"].apply(float) / 100000
    )
    D2 = {
        carrefour_stations.loc[id, "ID"]: (
            carrefour_stations.loc[id, "Latitude"],
            carrefour_stations.loc[id, "Longitude"],
        )
        for id in carrefour_stations.index
    }

    # Liste des concurrents dans un rayon de 10 km
    D = dict()

    def list_concurrents(id):
        L_conc = list()
        for x in D1:
            d = haversine(D2[id][0], D2[id][1], D1[x][0], D1[x][1])
            if d <= radius:
                L_conc.append(x)
        return L_conc

    # Créer un dictionnaire pour stocker les concurrents
    D = {id: list_concurrents(id) for id in D2}

    # Sauvegarder les données dans un fichier JSON
    with open(
        f"exam_florian_brunel/data/concurrents_{radius}km.json", "w"
    ) as json_file:
        json.dump(D, json_file, indent=4)
