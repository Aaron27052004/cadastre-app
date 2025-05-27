import streamlit as st
import os
import requests
import json

# Configuration API Google Maps : récupération de la clé API dans les variables d'environnement
#GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Fonction pour obtenir les coordonnées GPS à partir d'une adresse via Google Maps API
def get_coordinates(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            # Extraction de la latitude et longitude dans la réponse JSON
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
    # Si erreur ou pas de résultat, on renvoie None, None
    return None, None

# Fonction pour obtenir le numéro de cadastre à partir des coordonnées GPS via API IGN
def get_numero_cadastre(latitude, longitude):
    try:
        # Conversion en float pour assurer la bonne format des coordonnées
        longitude = float(longitude)
        latitude = float(latitude)

        # Création de l'objet géométrique au format GeoJSON (longitude en premier)
        geom = {
            "type": "Point",
            "coordinates": [longitude, latitude]
        }

        # Conversion de l'objet en chaîne JSON
        geom_json = json.dumps(geom)

        # URL de base de l'API cadastre IGN
        base_url = "https://apicarto.ign.fr/api/cadastre/parcelle"

        # Construction de l'URL complète avec paramètre geom encodé
        url = f"{base_url}?geom={requests.utils.quote(geom_json)}"

        # Requête HTTP GET avec header pour recevoir du JSON
        response = requests.get(url, headers={"Accept": "application/json"})

        # Si la réponse est OK, on tente d'extraire le numéro de cadastre
        if response.status_code == 200:
            data = response.json()
            
            try:
                commune= data['features'][0]['properties']['code_com']
                section = data['features'][0]['properties']['section']
                numero = data['features'][0]['properties']['numero']  
                numero_complet = f"{commune}-{section}-{numero}"     
                return numero_complet
            except (IndexError, KeyError):
                return None
        else:
            return None

    except Exception:
        return None

# Titre de l'application Streamlit
st.title("Recherche numéro de cadastre")

# Input utilisateur pour saisir une adresse
adresse = st.text_input("Entrez une adresse :")

# Si l'adresse est renseignée, on lance la recherche
if adresse:
    latitude, longitude = get_coordinates(adresse)  # On récupère latitude et longitude

    if latitude is not None and longitude is not None:  # Si on a bien les coordonnées
        #st.success(f"Coordonnées GPS trouvées : {latitude}, {longitude}")

        numero_cadastre = get_numero_cadastre(latitude, longitude)  # Recherche numéro de cadastre
        if numero_cadastre:
            st.success(f"Le numéro de cadastre est : {numero_cadastre}")
        else:
            st.error("Aucun numéro de cadastre trouvé pour ces coordonnées.")
    else:
        st.error("Aucune coordonnée trouvée pour cette adresse.")
