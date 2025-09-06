import React from 'react';

/**
 * The main landing page for the dashboard.
 *
 * Provides a welcome message and a link to the main map page.
 * @returns {React.ReactElement} The home page component.
 */
export default function Home() {
  return (
    <div style={{ padding: 24 }}>
      <h1>Civic Dashboard</h1>
      <p>Use the map page to view live issues.</p>
      <a href="/map">Open Map</a>
    </div>
  );
}
