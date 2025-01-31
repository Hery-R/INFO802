from flask import Flask, request, render_template
import folium
import requests
import math
from zeep import Client

app = Flask(__name__, template_folder='.')

def get_route_data(start_lat, start_lon, end_lat, end_lon):
    url = 'http://localhost:5012/map'
    params = {
        'start_lat': start_lat,
        'start_lon': start_lon,
        'end_lat': end_lat,
        'end_lon': end_lon
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        route_data = response.json()
        return route_data['features'][0]['geometry']['coordinates']
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération du trajet : {e}")
        return None

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

def get_coordinates(city):
    if not city:
        return None
        
    url = 'http://localhost:5011/coordinates'
    try:
        response = requests.get(url, params={'city': city})
        response.raise_for_status()
        coordinates = response.json()
        return coordinates.get('coordinates', [None, None])
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération des coordonnées : {e}")
        return None

def get_vehicle_list():
    url = "http://localhost:5013/vehicles"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        return []

def get_vehicle_details(vehicle_id):
    if not vehicle_id:
        return None
        
    url = f"http://localhost:5013/vehicle/{vehicle_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération des détails du véhicule : {e}")
        return None
    
def get_optimal_charging_time(vehicle):
    connectors = vehicle['connectors']
    return min(connector['time'] for connector in connectors)

def get_price_and_time(distance, vehicle):
    if not distance or not vehicle:
        return None, None
    try:
        client = Client('http://localhost:8000/?wsdl')
        autonomy = int(vehicle['range']['chargetrip_range']['best'])
        recharge_time = int(vehicle['battery']['usable_kwh'])
        result = client.service.get_time_price(int(distance), autonomy, recharge_time)
        
        print("LOG time and price : ", result[0], result[1])
        return result[0], result[1]
    except Exception as e:
        print(f"Error calling SOAP service: {e}")
        return None, None

def calculate_route_distance(route_data):
    if not route_data:
        return 0
    return sum(
        math.sqrt((route_data[i+1][1]-route_data[i][1])**2 + 
                 (route_data[i+1][0]-route_data[i][0])**2) * 111
        for i in range(len(route_data)-1)
    )

def get_required_charges(total_distance, autonomy, safety_margin=0.8):
    if autonomy <= 0:
        return 0
    return math.ceil(total_distance / (autonomy * safety_margin))

def get_search_points(segment):
    if not segment:
        return []
    return [
        segment[idx] for idx in [
            j * len(segment) // 4 for j in range(1, 4)
        ] if idx < len(segment)
    ]

def find_nearest_station(point, search_radius=0.1):
    try:
        response = requests.get(
            'http://localhost:5010/charge-stations',
            params={
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
            station = find_nearest_station(point)
            if station and not is_duplicate_station(station, optimal_stations):
                optimal_stations.append(station)
                break
                
    return optimal_stations

def calculate_optimal_route(start_lat, start_lon, end_lat, end_lon, autonomy):
    if autonomy <= 0:
        return None, None

    route_data = get_route_data(start_lat, start_lon, end_lat, end_lon)
    if not route_data:
        return None, None

    total_distance = calculate_route_distance(route_data)
    number_charge_required = get_required_charges(total_distance, autonomy)
    
    if number_charge_required == 0:
        return route_data, []

    segments = split_route_data(route_data, number_charge_required + 1)
    optimal_stations = find_charging_stations(segments, number_charge_required)

    return route_data, optimal_stations

def create_map(start_lat, start_lon, end_lat, end_lon):
    min_lat, max_lat = sorted([start_lat, end_lat])
    min_lon, max_lon = sorted([start_lon, end_lon])
    return folium.Map(
        location=[(min_lat + max_lat) / 2, (min_lon + max_lon) / 2],
        zoom_start=6
    )

def add_route_to_map(map_obj, route_data, start_name, end_name, start_lat, start_lon, end_lat, end_lon):
    if route_data:
        polyline = [(coord[1], coord[0]) for coord in route_data]
        folium.PolyLine(polyline, color='blue', weight=3, opacity=0.8).add_to(map_obj)
        
        folium.Marker(
            [start_lat, start_lon],
            popup=f'Départ: {start_name}',
            icon=folium.Icon(color='green')
        ).add_to(map_obj)
        
        folium.Marker(
            [end_lat, end_lon],
            popup=f'Arrivée: {end_name}',
            icon=folium.Icon(color='red')
        ).add_to(map_obj)

def add_stations_to_map(map_obj, stations):
    for station in stations:
        folium.Marker(
            [station['lat'], station['lon']],
            popup=f"Borne: {station['name']}",
            icon=folium.Icon(color='orange', icon='plug', prefix='fa')
        ).add_to(map_obj)

def process_route_request(start, end, selected_vehicle_id):
    vehicle_details = get_vehicle_details(selected_vehicle_id)["vehicle"]
    autonomy = float(vehicle_details["range"]["chargetrip_range"]["best"])
    
    start_lat, start_lon = get_coordinates(start)
    end_lat, end_lon = get_coordinates(end)
    
    map_obj = create_map(start_lat, start_lon, end_lat, end_lon)
    route_data, optimal_stations = calculate_optimal_route(
        start_lat, start_lon, end_lat, end_lon, autonomy
    )
    
    if route_data:
        add_route_to_map(map_obj, route_data, start, end, start_lat, start_lon, end_lat, end_lon)
        add_stations_to_map(map_obj, optimal_stations)
        
        total_distance = calculate_route_distance(route_data)
        time, price = get_price_and_time(total_distance, vehicle_details)
        print("LOG time and price : ", time, price)
        
        return {
            'map': map_obj._repr_html_(),
            'distance': total_distance,
            'time': time,
            'price': price,
            'nb_stations': len(optimal_stations)
        }
    
    return None

def create_default_map():
    """Crée une carte par défaut centrée sur la France"""
    return folium.Map(
        location=[46.603354, 1.888334],
        zoom_start=6
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    vehicles = get_vehicle_list()['vehicles']
    print("LOG: vehicles", vehicles)
    
    if request.method == 'POST':
        result = process_route_request(
            request.form['start'],
            request.form['end'],
            request.form['vehicle']
        )
        if result:
            vehicle_details = get_vehicle_details(request.form['vehicle'])["vehicle"]
            optimal_charging_time = get_optimal_charging_time(vehicle_details)
            return render_template(
                'index.html',
                vehicles=vehicles,
                vehicle_details=vehicle_details,
                optimal_charging_time=optimal_charging_time,
                map=result['map'],
                distance=result['distance'],
                time=result['time'],
                price=result['price'],
                nb_stations=result['nb_stations']
            )

   
    default_map = create_default_map()
    return render_template('index.html', 
                         vehicles=vehicles, 
                         map=default_map._repr_html_(), 
                         vehicle_details=None)

if __name__ == '__main__':
    app.run(port=5000, debug=True)

