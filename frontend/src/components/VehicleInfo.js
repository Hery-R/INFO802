import React from 'react';

const VehicleInfo = ({ vehicleDetails, routeInfo }) => {
    if (!vehicleDetails) return null;

    const {
        naming,
        range,
        media
    } = vehicleDetails;

    const {
        distance,
        time,
        price,
        nb_stations: nbStations,
        optimalChargingTime
    } = routeInfo || {};

    return (
        <div className="vehicle-info">
            <h2>
                <i className="fas fa-car-side"></i> {naming.make} {naming.model}
            </h2>

            {distance && (
                <p>
                    <i className="fas fa-road"></i>
                    <strong>Distance : </strong> {Math.round(distance)} km
                </p>
            )}

            {range?.chargetrip_range?.best && (
                <p>
                    <i className="fas fa-battery-full"></i>
                    <strong>Autonomie : </strong> {range.chargetrip_range.best} km
                </p>
            )}

            {optimalChargingTime && (
                <p>
                    <i className="fas fa-charging-station"></i>
                    <strong>Temps de recharge : </strong> {optimalChargingTime} minutes
                </p>
            )}

            {media?.image?.url && (
                <img 
                    src={media.image.url}
                    alt={`${naming.make} ${naming.model}`}
                />
            )}

            {(time || price || nbStations) && (
                <div className="calculation">
                    {time && (
                        <p>
                            <i className="fas fa-clock"></i>
                            <strong>Temps estimé : </strong> {time} h
                        </p>
                    )}
                    {price && (
                        <p>
                            <i className="fas fa-euro-sign"></i>
                            <strong>Prix estimé : </strong> {price} €
                        </p>
                    )}
                    {nbStations && (
                        <p>
                            <i className="fas fa-plug"></i>
                            <strong>Nombre de stations : </strong> {nbStations}
                        </p>
                    )}
                </div>
            )}
        </div>
    );
};

export default VehicleInfo; 