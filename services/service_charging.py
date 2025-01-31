from flask import Flask, request
import requests

app = Flask(__name__)

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

@app.route("/charge-stations", methods=["GET", "POST"])
def charge_stations():
    start_lat = request.args.get('start_lat')
    start_lon = request.args.get('start_lon')
    end_lat = request.args.get('end_lat')
    end_lon = request.args.get('end_lon')
    stations = get_charging_stations(start_lat, start_lon, end_lat, end_lon)
    return {"stations": stations}

if __name__ == "__main__":
    app.run(debug=True, port=5010)
