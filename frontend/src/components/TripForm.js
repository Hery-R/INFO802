import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'https://chargingflask-drajetbaf6hvfddm.francecentral-01.azurewebsites.net';

const TripForm = ({ onSubmit, loading }) => {
    const [vehicles, setVehicles] = useState([]);
    const [formData, setFormData] = useState({
        vehicle: '',
        start: '',
        end: ''
    });
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchVehicles = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/api/vehicles`);
                setVehicles(response.data.vehicles);
            } catch (err) {
                setError('Erreur lors du chargement des véhicules');
            }
        };
        fetchVehicles();
    }, []);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!formData.vehicle || !formData.start || !formData.end) {
            setError('Veuillez remplir tous les champs');
            return;
        }
        setError('');
        onSubmit(formData);
    };

    return (
        <div className="form-container">
            <h2>Planifiez votre Voyage</h2>
            
            {error && (
                <div className="error-message">
                    <i className="fas fa-exclamation-circle"></i> {error}
                </div>
            )}
            
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="vehicle">
                        <i className="fas fa-car"></i> Choisissez votre véhicule :
                    </label>
                    <select
                        id="vehicle"
                        name="vehicle"
                        value={formData.vehicle}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Sélectionnez un véhicule</option>
                        {vehicles.map(vehicle => (
                            <option key={vehicle.id} value={vehicle.id}>
                                {vehicle.naming.make} {vehicle.naming.model}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="start">
                        <i className="fas fa-map-marker-alt"></i> Origine :
                    </label>
                    <input
                        type="text"
                        id="start"
                        name="start"
                        value={formData.start}
                        onChange={handleChange}
                        placeholder="Ville de départ"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="end">
                        <i className="fas fa-flag-checkered"></i> Destination :
                    </label>
                    <input
                        type="text"
                        id="end"
                        name="end"
                        value={formData.end}
                        onChange={handleChange}
                        placeholder="Ville d'arrivée"
                        required
                    />
                </div>

                {loading && (
                    <div className="loading">
                        <i className="fas fa-spinner"></i> Calcul en cours...
                    </div>
                )}

                <button type="submit" disabled={loading}>
                    <i className="fas fa-route"></i> Calculer l'itinéraire
                </button>
            </form>
        </div>
    );
};

export default TripForm; 