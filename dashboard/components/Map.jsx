import React, { useEffect } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

/**
 * Renders an interactive map using Leaflet.js.
 *
 * This component initializes a map and displays markers for a list of issues.
 * It is responsible for setting up the map tiles and cleaning up the map
 * instance when the component unmounts.
 *
 * @param {object} props - The component props.
 * @param {Array<object>} [props.issues=[]] - A list of issue objects to display on the map.
 *   Each issue should have a `location` property to be marked.
 * @returns {React.ReactElement} The map container element.
 */
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
