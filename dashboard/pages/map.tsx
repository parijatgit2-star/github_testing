import dynamic from 'next/dynamic';
import React, { useEffect, useState } from 'react';

const MapNoSSR = dynamic(() => import('../../components/Map'), { ssr: false });

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
