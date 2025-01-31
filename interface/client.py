from flask import Flask, render_template, request
import requests
import folium

app = Flask(__name__, template_folder='.')

API_URL = "http://localhost:5000"

def get_vehicle_list():
    response = requests.get(f"{API_URL}/api/vehicles")
    return response.json()

def get_vehicle_details(vehicle_id):
    response = requests.get(f"{API_URL}/api/vehicle/{vehicle_id}")
    return response.json()

def process_route_request(start, end, vehicle_id):
    data = {
        "start": start,
        "end": end,
        "vehicle": vehicle_id
    }
    response = requests.post(f"{API_URL}/api/route", json=data)
    return response.json()

def get_optimal_charging_time(vehicle_details):
    connectors = vehicle_details['connectors']
    return min(connector['time'] for connector in connectors)

def create_default_map():
    response = requests.get(f"{API_URL}/api/default-map")
    return response.json()

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        vehicles = get_vehicle_list()['vehicles']
        print("LOG: vehicles", vehicles)
        
        if request.method == 'POST':
            result = process_route_request(
                request.form['start'],
                request.form['end'],
                request.form['vehicle']
            )
            if result and 'error' not in result:
                vehicle_details = get_vehicle_details(request.form['vehicle'])
                optimal_charging_time = get_optimal_charging_time(vehicle_details['vehicle_details'])
                return render_template(
                    'index.html',
                    vehicles=vehicles,
                    vehicle_details=vehicle_details['vehicle_details'],
                    optimal_charging_time=optimal_charging_time,
                    map=result['map'],
                    distance=result['distance'],
                    time=result['time'],
                    price=result['price'],
                    nb_stations=result['nb_stations']
                )
            else:
                error_message = result.get('error', 'Une erreur est survenue lors du calcul de l\'itinéraire')
                return render_template('index.html', 
                                    vehicles=vehicles,
                                    error=error_message)

        default_map = create_default_map()
        return render_template('index.html', 
                            vehicles=vehicles, 
                            map=default_map['map'], 
                            vehicle_details=None)
                            
    except Exception as e:
        print(f"Erreur : {str(e)}")
        return render_template('index.html', 
                            error="Une erreur est survenue lors de la communication avec l'API")

if __name__ == '__main__':
    app.run(port=5001, debug=True)


