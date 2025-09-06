import dynamic from 'next/dynamic';
import React, { useEffect, useState } from 'react';

const MapNoSSR = dynamic(() => import('../components/Map'), { ssr: false });

/**
 * Renders the main map page of the dashboard.
 *
 * This page dynamically loads the `Map` component to prevent server-side
 * rendering (SSR), which is incompatible with Leaflet. It fetches the list
 * of issues from the backend API and passes them to the map component.
 *
 * @returns {React.ReactElement} The map page component.
 */
export default function MapPage() {
  const [issues, setIssues] = useState([]);

  useEffect(() => {
    async function load() {
      const res = await fetch('http://localhost:4000/issues');
      const data = await res.json().catch(() => ({ data: [] }));
      setIssues(data || []);
    }
    load();
  }, []);

  return (
    <div style={{ height: '100vh' }}>
      <h2>Map</h2>
      <MapNoSSR issues={issues} />
    </div>
  );
}
