import React, { useState, useEffect } from 'react';

/**
 * A simple, responsive bar chart component rendered with SVG.
 * @param {object} props - The component props.
 * @param {Array<{label: string, value: number}>} [props.data=[]] - The data to display.
 * @returns {React.ReactElement} An SVG element representing the bar chart.
 */
function SimpleBarChart({ data = [] }) {
	const max = Math.max(...data.map(d => d.value), 1);
	return (
		<svg width="100%" height={200} viewBox={`0 0 500 200`} preserveAspectRatio="xMidYMid meet">
			{data.map((d, i) => {
				const barWidth = 40;
				const spacing = 15;
				const x = spacing + i * (barWidth + spacing);
				const h = (d.value / max) * 140;
				const y = 160 - h;
				return (
					<g key={i}>
						<rect x={x} y={y} width={barWidth} height={h} fill="#3b82f6" />
						<text x={x + barWidth / 2} y={176} fontSize={10} textAnchor="middle">{d.label}</text>
						<text x={x + barWidth / 2} y={y - 6} fontSize={12} textAnchor="middle">{d.value}</text>
					</g>
				);
			})}
		</svg>
	);
}

/**
 * The main analytics page for the dashboard.
 *
 * Fetches and displays analytics data from the backend.
 * @returns {React.ReactElement} The analytics page component.
 */
export default function Analytics() {
  const [issuesByTime, setIssuesByTime] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const res = await fetch('http://localhost:8000/admin/analytics/issues-by-time');
        if (!res.ok) {
          throw new Error('Failed to fetch analytics data');
        }
        const data = await res.json();
        // Transform data for the chart
        const chartData = data.map(item => ({
          label: new Date(item.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
          value: item.count,
        }));
        setIssuesByTime(chartData);
      } catch (err) {
        setError(err.message);
      }
    }
    fetchAnalytics();
  }, []);

	return (
		<div style={{ padding: 24 }}>
			<h1>Analytics</h1>

      <h2>Issues Reported Per Day (Last 7 Days)</h2>
			{error && <p style={{ color: 'red' }}>{error}</p>}
      <div style={{ maxWidth: 600, overflowX: 'auto' }}>
				<SimpleBarChart data={issuesByTime} />
			</div>
		</div>
	);
}
