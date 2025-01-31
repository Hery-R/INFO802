import requests, os
from dotenv import load_dotenv

load_dotenv()

def get_vehicle_list():
    url = "https://api.chargetrip.io/graphql"
    query = """
    query {
      vehicleList(page: 0, size: 20) {
        id
        naming {
          make
          model
        }
      }
    }
    """
    
    headers = {
        "Content-Type": "application/json",
        "x-client-id": os.getenv('CHARGETRIP_CLIENT_ID'),
        "x-app-id": os.getenv('CHARGETRIP_APP_ID')
    }
    
    data = {"query": query}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("LOG: get_vehicle_list", response.json()) 
        return response.json()["data"]["vehicleList"]
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        return []
    
def get_vehicle_details(vehicle_id):
    url = "https://api.chargetrip.io/graphql"
    query = """
        query vehicle($vehicleId: ID!) {
            vehicle(id: $vehicleId) {
                naming {
                    make
                    model
                    chargetrip_version
                }
                media {
                    image {
                        url
                    }
                }
                connectors {
                    standard
                    time
                }
                battery {
                    usable_kwh
                }
                range {
                    chargetrip_range {
                        best
                    }
                }
            }
        }
        """    
    
    headers = {
        "Content-Type": "application/json",
        "x-client-id": os.getenv('CHARGETRIP_CLIENT_ID'),
        "x-app-id": os.getenv('CHARGETRIP_APP_ID')
    }
    
    data = {"query": query, "variables": {"vehicleId": vehicle_id}}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["data"]["vehicle"]
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        return {}
    
    
