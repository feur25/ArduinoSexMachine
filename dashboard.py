import streamlit as st
import pandas as pd
import time
import requests  # Importer la bibliothèque requests pour effectuer des requêtes HTTP

# URL de votre API Flask
API_URL = 'http://localhost:5000/api/donnees'  # Remplacez 'localhost' par l'adresse IP de votre serveur si nécessaire

# Fonction pour charger les données depuis l'API
def load_data_from_api():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)
        else:
            st.error(f"Erreur lors de la récupération des données : {response.status_code}")
            return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur
    except Exception as e:
        st.error(f"Erreur lors de la connexion à l'API : {e}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur

# Conteneur pour l'affichage dynamique
placeholder = st.empty()

# Configuration de la fréquence de mise à jour
update_frequency = st.slider("Fréquence de mise à jour (secondes)", 1, 10, 1)

# Boucle pour mettre à jour le dashboard
while True:
    # Charger les données depuis l'API
    df = load_data_from_api()
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])  # Conversion en datetime
        df = df.sort_values('timestamp')

        # Calcul de l'occupation en temps réel
        df['occupation_change'] = df['type'].map({'entree': 1, 'sortie': -1}) * df['value']
        df['occupation'] = df['occupation_change'].cumsum()

        # Calcul des métriques
        total_entries = df[df['type'] == 'entree']['value'].sum()
        total_exits = df[df['type'] == 'sortie']['value'].sum()
        current_in_building = df['occupation'].iloc[-1]

        # Mettre à jour le dashboard
        with placeholder.container():
            # Affichage des métriques
            st.subheader("Statistiques en temps réel :")
            st.metric("Personnes dans le bâtiment", int(current_in_building))
            st.metric("Total entrées", int(total_entries))
            st.metric("Total sorties", int(total_exits))

            # Affichage des dernières données (ex. 20 dernières lignes)
            st.subheader("Dernières données :")
            st.write(df.tail(20))

            # Affichage d'un graphique dynamique de l'occupation
            st.subheader("Occupation en temps réel :")
            st.line_chart(df.set_index("timestamp")["occupation"])

    else:
        with placeholder.container():
            st.subheader("Aucune donnée disponible")
            st.write("En attente de données...")

    # Pause avant la prochaine mise à jour
    time.sleep(update_frequency)
