import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png';

const defaultIcon = L.icon({
    iconRetinaUrl: iconRetina,
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = defaultIcon;

const Map = ({ route, stations, startPoint, endPoint }) => {
    const center = [46.603354, 1.888334]; // Centre de la France

    useEffect(() => {
        console.log('Données de la carte:', { route, stations, startPoint, endPoint });
    }, [route, stations, startPoint, endPoint]);

    const stationIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
        shadowUrl: iconShadow,
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    const startIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
        shadowUrl: iconShadow,
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    const endIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        shadowUrl: iconShadow,
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    return (
        <div className="map-container">
            <MapContainer
                center={center}
                zoom={6}
                style={{ height: '100%', width: '100%' }}
            >
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                
                {route && Array.isArray(route) && route.length > 0 && (
                    <>
                        <Polyline 
                            positions={route}
                            color="#3498db"
                            weight={4}
                            opacity={0.8}
                            dashArray="10, 10"
                        >
                            <Tooltip sticky>Itinéraire recommandé</Tooltip>
                        </Polyline>
                    </>
                )}

                {startPoint && startPoint.lat && startPoint.lon && (
                    <Marker position={[startPoint.lat, startPoint.lon]} icon={startIcon}>
                        <Popup>
                            <div style={{ textAlign: 'center' }}>
                                <h3 style={{ margin: '5px 0', color: '#2980b9' }}>Point de départ</h3>
                                <p style={{ margin: '5px 0' }}>{startPoint.name}</p>
                            </div>
                        </Popup>
                    </Marker>
                )}

                {endPoint && endPoint.lat && endPoint.lon && (
                    <Marker position={[endPoint.lat, endPoint.lon]} icon={endIcon}>
                        <Popup>
                            <div style={{ textAlign: 'center' }}>
                                <h3 style={{ margin: '5px 0', color: '#c0392b' }}>Destination</h3>
                                <p style={{ margin: '5px 0' }}>{endPoint.name}</p>
                            </div>
                        </Popup>
                    </Marker>
                )}

                {stations && Array.isArray(stations) && stations.map((station, index) => {
                    if (!station.lat || !station.lon) return null;
                    return (
                        <Marker
                            key={index}
                            position={[station.lat, station.lon]}
                            icon={stationIcon}
                        >
                            <Popup>
                                <div style={{ textAlign: 'center' }}>
                                    <h3 style={{ margin: '5px 0', color: '#27ae60' }}>Station de recharge</h3>
                                    <p style={{ margin: '5px 0', fontWeight: 'bold' }}>{station.name}</p>
                                    {station.address && (
                                        <p style={{ margin: '5px 0', fontSize: '0.9em' }}>{station.address}</p>
                                    )}
                                </div>
                            </Popup>
                            <Tooltip direction="top" offset={[0, -35]} opacity={0.9}>
                                {station.name}
                            </Tooltip>
                        </Marker>
                    );
                })}
            </MapContainer>
        </div>
    );
};

export default Map; 