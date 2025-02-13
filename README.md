# INFO802
## Nom : RASOAMIARAMANANA Hery ny aina
## Description : Mini-projet pour INFO802


### Branches
- main : pour le tester localement
- master : pour la production sur azure

- [Voir le déploiement sur azure](https://proud-bay-09dfe3a1e.4.azurestaticapps.net)
- [Voir l'api flask sur azure](flaskapp-e0a6a8cxe9bmffdu.francecentral-01.azurewebsites.net)
    + "/api/vehicles" pour obtenir la liste des véhicules
- [Voir l'api soap sur azure](soap-fca9amdze0b7fudw.francecentral-01.azurewebsites.net)

### Technologies
- Python pour les services et l'API 
- React pour le frontend


### Installation
- lancer l'application app_soap.py (python 3.9 requis)
- lancer l'application app_flask.py
- lancer la commande npm install dans le dossier frontend
- lancer le serveur de développement avec npm start dans le dossier frontend


### Les routes de l'API

* `/api/vehicles` : pour obtenir la liste des véhicules via `["GET"]`
* `/api/vehicle/{vehicle_id}` : pour obtenir les détails d'un véhicule via `["GET"]`
* `/api/route` : pour calculer l'itinéraire ainsi que les données du genre le temps, le prix et les stations de recharge via `["POST"]`
	+ en spécifiant les coordonnées de départ et d'arrivée, ainsi que l'ID du véhicule
