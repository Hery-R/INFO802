from flask import Flask, render_template, request
import requests
import folium

app = Flask(__name__, template_folder='.')

API_URL = "http://localhost:5000"

def get_vehicle_list():
    response = requests.get(f"{API_URL}/api/vehicles")
    return response.json()

def get_vehicle_details(vehicle_id):
    print("LOG - Récupération des détails du véhicule :", vehicle_id)
    response = requests.get(f"{API_URL}/api/vehicle/{vehicle_id}")
    result = response.json()
    return result

def process_route_request(start, end, vehicle_id):
    data = {
        "start": start,
        "end": end,
        "vehicle": vehicle_id
    }
    response = requests.post(f"{API_URL}/api/route", json=data)
    result = response.json()
    return result

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
        
        if request.method == 'POST':
            print("LOG - Interface : Requête reçue pour", {
                "start": request.form['start'],
                "end": request.form['end'],
                "vehicle": request.form['vehicle']
            })
            
            result = process_route_request(
                request.form['start'],
                request.form['end'],
                request.form['vehicle']
            )
            
            if result and 'error' not in result:
                vehicle_details = get_vehicle_details(request.form['vehicle'])
                print("LOG - Interface : Résultat obtenu", {
                    "distance": result['distance'],
                    "time": result['time'],
                    "price": result['price'],
                    "stations": result['nb_stations']
                })
                
                return render_template(
                    'index.html',
                    vehicles=vehicles,
                    vehicle_details=vehicle_details['vehicle_details'],
                    optimal_charging_time=vehicle_details['optimal_charging_time'],
                    map=result['map'],
                    distance=result['distance'],
                    time=result['time'],
                    price=result['price'],
                    nb_stations=result['nb_stations']
                )
            else:
                error_message = result.get('error', 'Une erreur est survenue lors du calcul de l\'itinéraire')
                print("LOG - Interface : Erreur", error_message)
                return render_template('index.html', 
                                    vehicles=vehicles,
                                    error=error_message)

        default_map = create_default_map()
        return render_template('index.html', 
                            vehicles=vehicles, 
                            map=default_map['map'])
                            
    except Exception as e:
        print("LOG - Interface : Erreur critique", str(e))
        return render_template('index.html', 
                            error="Une erreur est survenue lors de la communication avec l'API")

if __name__ == '__main__':
    app.run(port=5001, debug=True)


