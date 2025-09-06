import React from 'react';

const dummy = [
	{ label: 'Potholes', value: 45 },
	{ label: 'Streetlight', value: 20 },
	{ label: 'Sanitation', value: 30 },
	{ label: 'Other', value: 15 },
];

function SimpleBarChart({ data = [] }) {
	const max = Math.max(...data.map(d => d.value), 1);
	return (
		<svg width="100%" height={200} viewBox={`0 0 400 200`} preserveAspectRatio="none">
			{data.map((d, i) => {
				const bw = 80;
				const x = 20 + i * (bw + 10);
				const h = (d.value / max) * 140;
				const y = 160 - h;
				return (
					<g key={i}>
						<rect x={x} y={y} width={bw} height={h} fill="#3b82f6" />
						<text x={x + bw / 2} y={176} fontSize={12} textAnchor="middle">{d.label}</text>
						<text x={x + bw / 2} y={y - 6} fontSize={12} textAnchor="middle">{d.value}</text>
					</g>
				);
			})}
		</svg>
	);
}

export default function Analytics() {
	return (
		<div style={{ padding: 24 }}>
			<h1>Analytics</h1>
			<p>Issue volume by category (sample)</p>
			<div style={{ maxWidth: 420 }}>
				<SimpleBarChart data={dummy} />
			</div>
		</div>
	);
}
