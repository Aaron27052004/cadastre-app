import streamlit as st
import requests
import os
import tempfile
from PIL import Image
from io import BytesIO
from fpdf import FPDF

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

def get_bbox(lat, lon, delta=0.002):
    # Construire un BBOX autour du point (lat, lon)
    # WMS 1.3.0 en EPSG:4326 utilise l'ordre : lat_min, lon_min, lat_max, lon_max
    return (lat - delta, lon - delta, lat + delta, lon + delta)

def get_wms_image(bbox, width=800, height=800):
    base_url = "https://data.geopf.fr/wms-r"
    params = {
        'LAYERS': 'CADASTRALPARCELS.PARCELS',  # Vérifie le nom exact de la couche
        'FORMAT': 'image/png',
        'SERVICE': 'WMS',
        'VERSION': '1.3.0',
        'REQUEST': 'GetMap',
        'STYLES': '',
        'CRS': 'EPSG:4326',
        'BBOX': ','.join(map(str, bbox)),
        'WIDTH': width,
        'HEIGHT': height
    }
    response = requests.get(base_url, params=params)
    image = Image.open(BytesIO(response.content))
    return image


def create_pdf(image):
    pdf = FPDF()
    pdf.add_page()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
        image.save(tmp_img.name, format="PNG")
        tmp_img_path = tmp_img.name

    pdf.image(tmp_img_path, x=10, y=10, w=190)

    os.remove(tmp_img_path)

    # pdf.output(dest='S') retourne le PDF en bytes
    pdf_bytes = pdf.output(dest='S').encode('latin1')  # encodage nécessaire

    # On met ces bytes dans un BytesIO
    pdf_buffer = BytesIO(pdf_bytes)

    return pdf_buffer


# Titre de l'application Streamlit
st.title("Recherche des coordonnées GPS et affichage des parcelles cadastrales")

adresse = st.text_input("Entrez une adresse :")

if adresse:
    latitude, longitude = get_coordinates(adresse)
    if latitude is not None and longitude is not None:
        #st.success(f"Coordonnées GPS trouvées : {latitude}, {longitude}")

        bbox = get_bbox(latitude, longitude)
        image = get_wms_image(bbox)

        st.image(image, caption="Parcelles cadastrales autour de l'adresse", use_container_width=True)
        
        pdf_file = create_pdf(image)
        st.download_button(
            label="Télécharger la carte en PDF",
            data=pdf_file,
            file_name=f"carte_cadastrale_{adresse}.pdf",
            mime="application/pdf"
        )

    else:
        st.error("Aucune coordonnée trouvée pour cette adresse.")

