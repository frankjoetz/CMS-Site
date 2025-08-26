async function fetchJSON(url) {
	const response = await fetch(url);
	if (!response.ok) throw new Error('Failed to fetch ' + url);
	return response.json();
}

async function initDashboard() {
	try {
		const summary = await fetchJSON('/api/dashboard/summary');
		document.getElementById('card-pendings').innerText = summary.pendingCount;
		document.getElementById('card-low-stock').innerText = summary.lowStockCount;
		document.getElementById('card-inventory-value').innerText = summary.totalInventoryValueFormatted;

		const ctxMonthly = document.getElementById('chart-monthly-po');
		new Chart(ctxMonthly, {
			type: 'bar',
			data: {
				labels: summary.monthly.labels,
				datasets: [{
					label: 'PO Cost (last 6 months)',
					data: summary.monthly.data,
					backgroundColor: '#60a5fa'
				}]
			},
			options: {responsive: true, maintainAspectRatio: false}
		});

		const ctxDaily = document.getElementById('chart-daily-receipts');
		new Chart(ctxDaily, {
			type: 'line',
			data: {
				labels: summary.daily.labels,
				datasets: [{
					label: 'Deliveries (last 14 days)',
					data: summary.daily.data,
					borderColor: '#22c55e'
				}]
			},
			options: {responsive: true, maintainAspectRatio: false}
		});

	} catch (err) {
		console.error(err);
	}
}

if (document.getElementById('chart-monthly-po')) {
	initDashboard();
}