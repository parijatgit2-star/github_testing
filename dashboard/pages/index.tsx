import React, { useState, useEffect } from 'react';
import Link from 'next/link';

/**
 * The main landing page for the dashboard.
 *
 * Fetches and displays a list of all reported issues in a table.
 * @returns {React.ReactElement} The home page component.
 */
export default function Home() {
  const [issues, setIssues] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchIssues() {
      try {
        const res = await fetch('http://localhost:8000/issues');
        if (!res.ok) {
          const errorText = await res.text();
          throw new Error(`Failed to fetch issues: ${res.status} ${errorText}`);
        }
        const data = await res.json();
        setIssues(data);
      } catch (err) {
        setError(err.message);
        console.error(err);
      }
    }
    fetchIssues();
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h1>Civic Dashboard</h1>
      <p>A list of all reported issues.</p>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ddd', padding: 8, textAlign: 'left' }}>Title</th>
            <th style={{ border: '1px solid #ddd', padding: 8, textAlign: 'left' }}>Status</th>
            <th style={{ border: '1px solid #ddd', padding: 8, textAlign: 'left' }}>Date</th>
          </tr>
        </thead>
        <tbody>
          {issues.map((issue) => (
            <tr key={issue.id}>
              <td style={{ border: '1px solid #ddd', padding: 8 }}>
                <Link href={`/issues/${issue.id}`} style={{ color: 'blue' }}>
                  {issue.title}
                </Link>
              </td>
              <td style={{ border: '1px solid #ddd', padding: 8 }}>{issue.status}</td>
              <td style={{ border: '1px solid #ddd', padding: 8 }}>
                {new Date(issue.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
