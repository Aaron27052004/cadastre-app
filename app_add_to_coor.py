import streamlit as st
import requests


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

# Titre de l'application Streamlit
st.title("Recherche des coordonées GPS")

# Input utilisateur pour saisir une adresse
adresse = st.text_input("Entrez une adresse :")

if adresse :
    latitude, longitude = get_coordinates(adresse)

    if latitude is not None and longitude is not None:
        st.success(f"Coordonnées GPS trouvées : {latitude}, {longitude}")
    else:
        st.error("Aucune coordonnée trouvée pour cette adresse.")