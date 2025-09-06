import React, { useEffect } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

export default function Map({ issues = [] }) {
  useEffect(() => {
    const map = L.map('map').setView([0, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    issues.forEach(issue => {
      if (issue.location) {
        // location is geography(point) - we will skip parsing here in scaffold
      }
    });

    return () => map.remove();
  }, [issues]);

  return <div id="map" style={{ height: '90vh', width: '100%' }} />;
}
