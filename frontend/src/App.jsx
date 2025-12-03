import React, { useState } from 'react';
import Viewer from './components/Viewer';
import './App.css';

function App() {
    const [file, setFile] = useState(null);
    const [glbUrl, setGlbUrl] = useState(null);
    const [features, setFeatures] = useState({});
    const [loading, setLoading] = useState(false);
    const [selectedFeature, setSelectedFeature] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Use environment variable for API URL
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/analyze`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Analysis failed');

            const data = await response.json();
            setGlbUrl(data.glb_url);
            setFeatures(data.features);
        } catch (error) {
            console.error(error);
            alert('Error analyzing file');
        } finally {
            setLoading(false);
        }
    };

    const handleFeatureSelect = (faceId, type) => {
        setSelectedFeature({ id: faceId, type: type });
    };

    return (
        <div className="app-container">
            <div className="sidebar">
                <h2>BrepMFR</h2>
                <div className="upload-section">
                    <input type="file" accept=".stp,.step" onChange={handleFileChange} />
                    <button onClick={handleUpload} disabled={!file || loading}>
                        {loading ? 'Analyzing...' : 'Analyze'}
                    </button>
                </div>

                <div className="feature-list">
                    <h3>Detected Features</h3>
                    <ul>
                        {Object.entries(features).map(([faceId, type]) => (
                            <li
                                key={faceId}
                                className={selectedFeature?.id === faceId ? 'selected' : ''}
                                onClick={() => handleFeatureSelect(faceId, type)}
                            >
                                <strong>{type}</strong> ({faceId})
                            </li>
                        ))}
                    </ul>
                </div>

                {selectedFeature && (
                    <div className="info-panel">
                        <h4>Selected Face</h4>
                        <p>ID: {selectedFeature.id}</p>
                        <p>Type: {selectedFeature.type}</p>
                    </div>
                )}
            </div>

            <div className="viewer-container">
                {glbUrl ? (
                    <Viewer glbUrl={glbUrl} features={features} onFeatureSelect={handleFeatureSelect} />
                ) : (
                    <div className="placeholder">
                        <p>Upload a STEP file to visualize</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
