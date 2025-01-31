import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Map from './components/Map';
import TripForm from './components/TripForm';
import VehicleInfo from './components/VehicleInfo';

const App = () => {
    const [loading, setLoading] = useState(false);
    const [vehicleDetails, setVehicleDetails] = useState(() => {
        const saved = localStorage.getItem('vehicleDetails');
        return saved ? JSON.parse(saved) : null;
    });
    const [routeInfo, setRouteInfo] = useState(() => {
        const saved = localStorage.getItem('routeInfo');
        return saved ? JSON.parse(saved) : null;
    });
    const [mapData, setMapData] = useState(() => {
        const saved = localStorage.getItem('mapData');
        return saved ? JSON.parse(saved) : {
            route: null,
            stations: null,
            startPoint: null,
            endPoint: null
        };
    });

    // Sauvegarder les données dans localStorage quand elles changent
    useEffect(() => {
        if (vehicleDetails) {
            localStorage.setItem('vehicleDetails', JSON.stringify(vehicleDetails));
        }
    }, [vehicleDetails]);

    useEffect(() => {
        if (routeInfo) {
            localStorage.setItem('routeInfo', JSON.stringify(routeInfo));
        }
    }, [routeInfo]);

    useEffect(() => {
        if (mapData) {
            localStorage.setItem('mapData', JSON.stringify(mapData));
        }
    }, [mapData]);

    const handleFormSubmit = async (formData) => {
        setLoading(true);
        try {
            // Récupération des détails du véhicule
            const vehicleResponse = await axios.get(`/api/vehicle/${formData.vehicle}`);
            setVehicleDetails(vehicleResponse.data.vehicle_details);

            // Calcul de l'itinéraire
            const routeResponse = await axios.post('/api/route', {
                start: formData.start,
                end: formData.end,
                vehicle: formData.vehicle
            });

            // Mise à jour des informations de route
            setRouteInfo({
                distance: routeResponse.data.distance,
                time: routeResponse.data.time,
                price: routeResponse.data.price,
                nbStations: routeResponse.data.nb_stations,
                optimalChargingTime: vehicleResponse.data.optimal_charging_time
            });

            // Mise à jour des données de la carte
            if (routeResponse.data.route) {
                setMapData({
                    route: routeResponse.data.route,
                    stations: routeResponse.data.stations,
                    startPoint: routeResponse.data.startPoint,
                    endPoint: routeResponse.data.endPoint
                });
            }
        } catch (error) {
            console.error('Erreur lors du calcul de l\'itinéraire:', error);
            if (error.response) {
                console.error('Données de l\'erreur:', error.response.data);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <Map {...mapData} />
            <TripForm onSubmit={handleFormSubmit} loading={loading} />
            {vehicleDetails && (
                <VehicleInfo
                    vehicleDetails={vehicleDetails}
                    routeInfo={routeInfo}
                />
            )}
        </div>
    );
};

export default App; 