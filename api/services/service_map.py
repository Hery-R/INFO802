import requests, os
from dotenv import load_dotenv

load_dotenv()
def get_map(start_lat, start_lon, end_lat, end_lon):
    ORS_API_KEY = os.getenv('ORS_API_KEY')
    route_url = f"https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {"Authorization": ORS_API_KEY}
    params = {"start": f"{start_lon},{start_lat}", "end": f"{end_lon},{end_lat}"}
    
    try:
        route_response = requests.get(route_url, headers=headers, params=params)
        route_response.raise_for_status()
        route_data = route_response.json()
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération du trajet : {e}")
        route_data = {}

    return route_data

def get_route_data(start_lat, start_lon, end_lat, end_lon):
    route_data = get_map(start_lat, start_lon, end_lat, end_lon)
    return route_data['features'][0]['geometry']['coordinates']
