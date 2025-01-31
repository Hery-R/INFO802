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
        response = requests.get(
            'https://odre.opendatasoft.com/api/records/1.0/search/',
            params={
                "dataset": "bornes-irve",
                "q": "",
                'start_lat': point[1] - search_radius,
                'start_lon': point[0] - search_radius,
                'end_lat': point[1] + search_radius,
                'end_lon': point[0] + search_radius
            }
        )
        response.raise_for_status()
        stations = response.json()
        
        if stations.get('stations', {}).get('records'):
            station = stations['stations']['records'][0]
            return {
                'lat': float(station['fields']['ylatitude']),
                'lon': float(station['fields']['xlongitude']),
                'name': station['fields'].get('n_station', 'Station inconnue')
            }
    except requests.RequestException as e:
        print(f"Erreur lors de la recherche des bornes: {e}")
    return None

