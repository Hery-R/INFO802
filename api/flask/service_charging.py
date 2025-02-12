import requests


def get_charging_stations(start_lat, start_lon, end_lat, end_lon):
    url = 'https://odre.opendatasoft.com/api/records/1.0/search/'
    params = {
        "dataset": "bornes-irve",
        "q": "",
        "rows": 10000,
        "geofilter.bbox": f"{start_lat},{start_lon},{end_lat},{end_lon}"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération des bornes : {e}")
        return {"results": []}
    

def find_nearest_station(point, search_radius=0.1):
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

