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
    // Default view if no issues have locations
    let initialView = [20, 0];
    let initialZoom = 2;

    const locatedIssues = issues.filter(issue => issue.location);
    if (locatedIssues.length > 0) {
      const firstLocation = locatedIssues[0].location.split(',');
      initialView = [parseFloat(firstLocation[0]), parseFloat(firstLocation[1])];
      initialZoom = 13;
    }

    const map = L.map('map').setView(initialView, initialZoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    locatedIssues.forEach(issue => {
      const [lat, lon] = issue.location.split(',');
      if (!isNaN(lat) && !isNaN(lon)) {
        const marker = L.marker([parseFloat(lat), parseFloat(lon)]).addTo(map);
        const popupContent = `
          <b>${issue.title}</b>
          <br>${issue.status}
          <br><a href="/issues/${issue.id}">View Details</a>
        `;
        marker.bindPopup(popupContent);
      }
    });

    return () => map.remove();
  }, [issues]);

  return <div id="map" style={{ height: '90vh', width: '100%' }} />;
}
