import requests


def find_nearest_station(point, search_radius=0.1):
    """Trouve la borne la plus proche de la position donnée 
    utilise l'API OpenDataSoft pour récupérer les bornes"""
    try:
        lat, lon = point[1], point[0]
        bbox = f"{lat - search_radius},{lon - search_radius},{lat + search_radius},{lon + search_radius}"
        
        response = requests.get(
            'https://odre.opendatasoft.com/api/records/1.0/search/',
            params={
                "dataset": "bornes-irve",
                "rows": 1,
                "geofilter.bbox": bbox
            }
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get('records') and len(data['records']) > 0:
            station = data['records'][0]
            result = {
                'lat': float(station['fields']['ylatitude']),
                'lon': float(station['fields']['xlongitude']),
                'name': station['fields'].get('n_station', 'Station inconnue')
            }
            return result
            
        return None
        
    except Exception as e:
        print(f"Erreur lors de la recherche des bornes: {e}")
        return None

