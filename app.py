import streamlit as st
import requests
import json

#titre de l'application
st.title("Recherche numéro de cadastre")

#on recupère l'adresse ou les coordonnées
longitude = st.text_input("Longitude")
latitude = st.text_input("Latitude")

if longitude and latitude: #si ils ne sont pas vides
    try:
        #on transforme en float
        # pour éviter les erreurs de conversion
        longitude = float(longitude)
        latitude = float(latitude)

        #on creer le tableau de données pour covertir apres en json
        geom = {
            "type": "Point",
            "coordinates": [longitude, latitude]
        }

        #on convertit en json
        geom_json = json.dumps(geom)

        #URL de base de l'API
        base_url="https://apicarto.ign.fr/api/cadastre/parcelle"

        #Construction de l'URL complète avec le paramètre geom encodé
        url=f"{base_url}?geom={requests.utils.quote(geom_json)}"

        #on fait la requete avec get et on recupere la réponse avec le header pour le format JSON
        response = requests.get(url, headers={"Accept": "application/json"})

        #on recupère le code de statut de la réponse
        http_status = response.status_code

        if http_status == 200: #si la requete est ok
            #on recupère les données en json
            data = response.json()
            
            try:
                #on recupère le numéro de cadastre 
                numero_cadastre=data['features'][0]['properties']['numero']

                #affichage du numéro de cadastre
                st.success(f"Le numéro de cadastre est : {numero_cadastre}")
            except (IndexError, KeyError):
                st.error("Aucun numéro de cadastre trouvé pour ces coordonnées.")

        #autre code de statut
        else:
            st.error(f"Erreur API : code {http_status}")

    #si les coordonées sont non valides
    except ValueError:
        st.error("Merci d’entrer des nombres valides pour longitude et latitude.")

    except Exception as e:
        st.error(f"Erreur : {e}")