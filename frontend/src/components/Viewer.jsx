import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { useGLTF, OrbitControls, Stage } from '@react-three/drei';
import * as THREE from 'three';

function Model({ url, features, onFaceClick }) {
    const { scene } = useGLTF(url);
    const [hovered, setHover] = useState(null);

    useEffect(() => {
        scene.traverse((child) => {
            if (child.isMesh) {
                // Ensure unique material for each face to allow individual coloring
                child.material = child.material.clone();
                child.material.side = THREE.DoubleSide;

                // Check if this mesh corresponds to a known feature
                // Assuming mesh names match Face_IDs from backend
                const featureType = features[child.name];
                if (featureType) {
                    // Apply color based on feature type
                    const color = getColorForFeature(featureType);
                    child.material.color.set(color);
                    child.userData.originalColor = color;
                } else {
                    child.userData.originalColor = '#cccccc'; // Default
                    child.material.color.set('#cccccc');
                }
            }
        });
    }, [scene, features]);

    useFrame((state) => {
        // Optional: Animation or updates
    });

    return (
        <primitive
            object={scene}
            onPointerOver={(e) => {
                e.stopPropagation();
                setHover(e.object.name);
                e.object.material.color.set('orange'); // Highlight color
            }}
            onPointerOut={(e) => {
                e.stopPropagation();
                setHover(null);
                // Restore original color
                e.object.material.color.set(e.object.userData.originalColor || '#cccccc');
            }}
            onClick={(e) => {
                e.stopPropagation();
                onFaceClick(e.object.name, features[e.object.name]);
            }}
        />
    );
}

function getColorForFeature(type) {
    const colors = {
        'Hole': '#ff0000',
        'Slot': '#00ff00',
        'Plane': '#0000ff',
        'Chamfer': '#ffff00',
        'Cylinder': '#00ffff',
        // Add more mappings
    };
    return colors[type] || '#888888';
}

export default function Viewer({ glbUrl, features, onFeatureSelect }) {
    return (
        <div style={{ width: '100%', height: '100%' }}>
            <Canvas shadows dpr={[1, 2]} camera={{ fov: 50 }}>
                <Stage environment="city" intensity={0.6}>
                    {glbUrl && <Model url={glbUrl} features={features} onFaceClick={onFeatureSelect} />}
                </Stage>
                <OrbitControls makeDefault />
            </Canvas>
        </div>
    );
}
