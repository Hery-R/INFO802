from flask import Flask, request, render_template
from zeep import Client
import requests
import math
import service_map as mp
import service_city as ct
import service_vehicle as vh
import service_charging as ch
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin

# Mettre à jour l'URL avec votre service SOAP déployé
SOAP_URL = 'https://soap-fca9amdze0b7fudw.francecentral-01.azurewebsites.net/soap'

# Route de test pour vérifier que l'application fonctionne
@app.route('/')
def home():
    return "Flask API opérationnelle"

def split_route_data(route_data, n):
    if not route_data or n <= 0:
        return {}
    length = len(route_data)
    min_length = math.floor(length / n)
    remainder = length % n
    result = {}
    start = 0

    for i in range(n):
        sub_length = min_length + (1 if i < remainder else 0)
        end = start + sub_length
        result[i] = route_data[start:end]
        start = end

    return result

    
def get_optimal_charging_time(vehicle):
    connectors = vehicle['connectors']
    return min(connector['time'] for connector in connectors)

def get_price_and_time(distance, vehicle):
    try:
        autonomy = float(vehicle['range']['chargetrip_range']['best'])
        recharge_time = float(vehicle['battery']['usable_kwh'])
        distance = float(distance)
        client = Client(f'{SOAP_URL}?wsdl')
        result = client.service.get_time_price(distance, autonomy, recharge_time)
        print("LOG - time", result[0], "price", result[1])
        return round(float(result[0]), 2), round(float(result[1]), 2)
    except Exception as e:
        print(f"Erreur dans get_price_and_time : {str(e)}")
        return None, None
        
        

def calculate_route_distance(route_data):
    if not route_data:
        return 0
    return sum(
        math.sqrt((route_data[i+1][1]-route_data[i][1])**2 + 
                 (route_data[i+1][0]-route_data[i][0])**2) * 111
        for i in range(len(route_data)-1)
    )

def get_required_charges(total_distance, autonomy, safety_margin=0.8, max_charges=10):
    if autonomy <= 0:
        return 0
    required_charges = math.ceil(total_distance / (autonomy * safety_margin))
    required_charges = min(required_charges, max_charges)
    return required_charges

def get_search_points(segment):
    if not segment:
        return []
    return [
        segment[idx] for idx in [
            j * len(segment) // 4 for j in range(1, 4)
        ] if idx < len(segment)
    ]

def is_duplicate_station(station, existing_stations, threshold=0.0001):
    return any(
        abs(s['lat'] - station['lat']) < threshold and 
        abs(s['lon'] - station['lon']) < threshold 
        for s in existing_stations
    )

def find_charging_stations(segments, number_charge_required):
    optimal_stations = []
    
    for i in range(number_charge_required):
        if i not in segments:
            continue
            
        search_points = get_search_points(segments[i])
        for point in search_points:
            station = ch.find_nearest_station(point)
            if station and not is_duplicate_station(station, optimal_stations):
                optimal_stations.append(station)
                break
                
    return optimal_stations

def calculate_optimal_route(start_lat, start_lon, end_lat, end_lon, autonomy):
    if autonomy <= 0:
        return None, None

    route_data = mp.get_route_data(start_lat, start_lon, end_lat, end_lon)
    if not route_data:
        return None, None

    total_distance = calculate_route_distance(route_data)
    number_charge_required = get_required_charges(total_distance, autonomy)
    
    if number_charge_required == 0:
        return route_data, []

    segments = split_route_data(route_data, number_charge_required + 1)
    optimal_stations = find_charging_stations(segments, number_charge_required)

    return route_data, optimal_stations



def process_route_request(start, end, selected_vehicle_id):
    try:
        vehicle_details = vh.get_vehicle_details(selected_vehicle_id)
        autonomy = float(vehicle_details["range"]["chargetrip_range"]["best"])
        
        start_lat, start_lon = ct.get_coordinates(start)
        end_lat, end_lon = ct.get_coordinates(end)
        
        route_data, optimal_stations = calculate_optimal_route(
            start_lat, start_lon, end_lat, end_lon, autonomy
        )
        
        if route_data:
            total_distance = calculate_route_distance(route_data)
            time, price = get_price_and_time(total_distance, vehicle_details)
            
            # Conversion des coordonnées de la route pour Leaflet (de [lon, lat] à [lat, lon])
            formatted_route = [[coord[1], coord[0]] for coord in route_data]
            
            # Formatage des stations pour le frontend
            formatted_stations = [{
                'lat': station['lat'],
                'lon': station['lon'],
                'name': station.get('name', 'Station de recharge'),
                'address': station.get('address', '')
            } for station in optimal_stations]
            
            # Formatage des points de départ et d'arrivée
            start_point = {
                'lat': start_lat,
                'lon': start_lon,
                'name': start
            }
            
            end_point = {
                'lat': end_lat,
                'lon': end_lon,
                'name': end
            }
            
            return {
                'route': formatted_route,  # Liste de coordonnées [lat, lon] pour Leaflet
                'stations': formatted_stations,
                'startPoint': start_point,
                'endPoint': end_point,
                'distance': total_distance,
                'time': time,
                'price': price,
                'nb_stations': len(optimal_stations)
            }
        
        return None
    except Exception as e:
        print(f"Erreur dans process_route_request: {str(e)}")
        return None



@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    """Route pour obtenir la liste des véhicules"""
    vehicles = vh.get_vehicle_list()
    return {'vehicles': vehicles}

@app.route('/api/vehicle/<vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    """Route pour obtenir les détails d'un véhicule spécifique"""
    vehicle_details = vh.get_vehicle_details(vehicle_id)
    optimal_charging_time = get_optimal_charging_time(vehicle_details)
    return {
        'vehicle_details': vehicle_details,
        'optimal_charging_time': optimal_charging_time
    }

@app.route('/api/route', methods=['POST'])
def calculate_route():
    """Route pour calculer l'itinéraire et les stations de recharge"""
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')
    vehicle_id = data.get('vehicle')
    
    if not all([start, end, vehicle_id]):
        return {'error': 'Paramètres manquants'}, 400
        
    result = process_route_request(start, end, vehicle_id)
    if result:
        return result
    return {'error': 'Impossible de calculer l\'itinéraire'}, 400

@app.route('/api/charging-time', methods=['POST'])
def calculate_charging_details():
    """Route pour calculer le temps et le prix de recharge"""
    data = request.get_json()
    distance = data.get('distance')
    vehicle_id = data.get('vehicle')
    
    if not all([distance, vehicle_id]):
        return {'error': 'Paramètres manquants'}, 400
        
    vehicle_details = vh.get_vehicle_details(vehicle_id)["vehicle"]
    time, price = get_price_and_time(distance, vehicle_details)
    
    return {
        'charging_time': time,
        'price': price
    }

# Point d'entrée pour Azure
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

