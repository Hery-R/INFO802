from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

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


@app.route('/map', methods=['GET'])
def map():
    start_lat = request.args.get('start_lat')
    start_lon = request.args.get('start_lon')
    end_lat = request.args.get('end_lat')
    end_lon = request.args.get('end_lon')
    
    route_data = get_map(start_lat, start_lon, end_lat, end_lon)
    return jsonify(route_data)

if __name__ == '__main__':
    app.run(debug=True, port=5012)