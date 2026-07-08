let _chart = null
let _drawZones = false



const BASE_OPTS = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 350 },
    interaction: { mode: 'index', intersect: false },
    plugins: {
        legend: { display: false },
        tooltip: {
            backgroundColor: 'rgba(10,20,11,0.96)',
            borderColor: 'rgba(26,44,28,1)',
            borderWidth: 1,
            titleColor: '#cce0cc',
            bodyColor: '#7a9e7a',
            titleFont: { family: "'JetBrains Mono'", size: 11 },
            bodyFont: { family: "'JetBrains Mono'", size: 10 },
            padding: 10,
            caretSize: 4
        }
    },

    scales: {
        x: {
            ticks: {
                color: '#3a5c3a',
                font: { family: "'JetBrains Mono'", size: 9 },
                maxTicksLimit: 10,
                maxRotation: 0
            },
            grid: { color: 'rgba(26,44,28,0.55)' },
            border: { color: '#1a2c1c' }
        },
        y: {
            ticks: {
                color: '#3a5c3a',
                font: { family: "'JetBrains Mono'", size: 9 }
            },
            grid: { color: 'rgba(26,44,28,0.55)' },
            border: { color: '#1a2c1c' }
        }
    }
}


const stressZonePlugin = {
    id: 'stressZones',
    beforeDatasetsDraw(chart) {
        if (!_drawZones) return

        const { ctx, chartArea: { left, right }, scales: { y } } = chart
        if (!y) return

        const zones = [
            { min: 55, max: 100, color: 'rgba(239,68,68,0.07)' },
            { min: 30, max: 55, color: 'rgba(251,146,60,0.07)' },
            { min: 10, max: 30, color: 'rgba(250,204,21,0.07)' },
            { min: 0, max: 10, color: 'rgba(74,222,128,0.07)' }
        ]

        zones.forEach(z => {
            const yT = y.getPixelForValue(Math.min(z.max, y.max))
            const yB = y.getPixelForValue(Math.max(z.min, y.min))
            ctx.save()
            ctx.fillStyle = z.color
            ctx.fillRect(left, yT, right - left, yB - yT)
            ctx.restore()
        })
    }
}





Chart.register(stressZonePlugin)



function fmtLabel(ts) {
    const d = new Date(ts)
    const dy = d.getDate().toString().padStart(2, '0')
    const mo = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getMonth()]
    const hr = d.getHours().toString().padStart(2, '0')
    const mn = d.getMinutes().toString().padStart(2, '0')
    return `${dy} ${mo} ${hr}:${mn}`
}

function pointColor(level) {
    const colors = {
        optimal: '#4ade80',
        mild: '#facc15',
        moderate: '#fb923c',
        severe: '#ef4444'
    }
    return colors[level] || '#3a5c3a'
}



function stressConfig(readings, labels, onPick) {
    _drawZones = true
    const data = readings.map(r => r.stress.overall_stress)
    const ptCol = readings.map(r => pointColor(r.stress.stress_level))

    return {
        type: 'line',
        data: {
            labels,
            datasets: [{
                data,
                borderColor: '#22c55e',
                backgroundColor: 'rgba(34,197,94,0.07)',
                pointBackgroundColor: ptCol,
                pointBorderColor: ptCol,
                pointRadius: 3,
                pointHoverRadius: 7,

                tension: 0.35,
                fill: true,
                borderWidth: 1.5
            }]
        },
        options: {
            ...BASE_OPTS,
            onClick: (e, els) => {
                if (els.length && onPick) onPick(els[0].index)
            },
            scales: {
                ...BASE_OPTS.scales,
                y: { ...BASE_OPTS.scales.y, min: 0, max: 100 }
            },
            plugins: {
                ...BASE_OPTS.plugins,
                tooltip: {
                    ...BASE_OPTS.plugins.tooltip,
                    callbacks: {
                        title: ctx => fmtLabel(readings[ctx[0].dataIndex].timestamp),
                        label: ctx => {

                            const r = readings[ctx.dataIndex]
                            return [
                                ` stress  : ${ctx.parsed.y.toFixed(1)}`,
                                ` level   : ${r.stress.stress_level}`,
                                ` dominant: ${r.stress.dominant_stress}`
                            ]
                        }
                    }
                }
            }
        }
    }
}

function climateConfig(readings, labels, onPick) {
    _drawZones = false
    return {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Temp (°C)',
                    data: readings.map(r => r.temperature_c),
                    borderColor: '#ef4444',
                    backgroundColor: 'transparent',
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    tension: 0.35,
                    borderWidth: 1.5,
                    yAxisID: 'y'
                },
                {
                    label: 'Humidity (%)',
                    data: readings.map(r => r.humidity_pct),
                    borderColor: '#38bdf8',
                    backgroundColor: 'transparent',
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    tension: 0.35,


                    borderWidth: 1.5,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            ...BASE_OPTS,
            onClick: (e, els) => {
                if (els.length && onPick) onPick(els[0].index)
            },
            scales: {
                x: BASE_OPTS.scales.x,
                y: { ...BASE_OPTS.scales.y, position: 'left' },


                y1: {
                    ...BASE_OPTS.scales.y,
                    position: 'right',
                    min: 0,
                    max: 100,
                    grid: { drawOnChartArea: false }
                }
            },
            plugins: {
                ...BASE_OPTS.plugins,
                legend: {
                    display: true,
                    labels: {
                        color: '#7a9e7a',
                        font: { family: "'JetBrains Mono'", size: 10 },
                        boxWidth: 10,
                        padding: 14
                    }
                },
                tooltip: {
                    ...BASE_OPTS.plugins.tooltip,
                    callbacks: {
                        title: ctx => fmtLabel(readings[ctx[0].dataIndex].timestamp)
                    }
                }
            }
        }
    }
}

function soilConfig(readings, labels, onPick) {
    _drawZones = false
    return {
        type: 'line',
        data: {
            labels,
            datasets: [{
                data: readings.map(r => r.soil_moisture_pct),
                borderColor: '#a78bfa',
                backgroundColor: 'rgba(167,139,250,0.07)',
                pointRadius: 2,
                pointHoverRadius: 5,
                tension: 0.35,
                fill: true,
                borderWidth: 1.5
            }]
        },
        options: {
            ...BASE_OPTS,
            onClick: (e, els) => {
                if (els.length && onPick) onPick(els[0].index)
            },
            scales: {
                x: BASE_OPTS.scales.x,
                y: { ...BASE_OPTS.scales.y, min: 0, max: 100 }
            },
            plugins: {
                ...BASE_OPTS.plugins,
                tooltip: {
                    ...BASE_OPTS.plugins.tooltip,
                    callbacks: {
                        title: ctx => fmtLabel(readings[ctx[0].dataIndex].timestamp),
                        label: ctx => ` soil: ${ctx.parsed.y.toFixed(1)} %`
                    }
                }
            }
        }
    }
}

function lightConfig(readings, labels, onPick) {
    _drawZones = false
    return {
        type: 'line',
        data: {
            labels,
            datasets: [{
                data: readings.map(r => r.light_lux),
                borderColor: '#fbbf24',
                backgroundColor: 'rgba(251,191,36,0.07)',
                pointRadius: 2,
                pointHoverRadius: 5,
                tension: 0.35,
                fill: true,
                borderWidth: 1.5
            }]
        },
        options: {
            ...BASE_OPTS,
            onClick: (e, els) => {
                if (els.length && onPick) onPick(els[0].index)
            },
            scales: {
                x: BASE_OPTS.scales.x,
                y: { ...BASE_OPTS.scales.y, min: 0 }
            },
            plugins: {
                ...BASE_OPTS.plugins,
                tooltip: {
                    ...BASE_OPTS.plugins.tooltip,

                    callbacks: {
                        title: ctx => fmtLabel(readings[ctx[0].dataIndex].timestamp),
                        label: ctx => ` light: ${Math.round(ctx.parsed.y).toLocaleString()} lux`
                    }
                }
            }
        }
    }
}

function initChart(readings, tab, onPick) {
    if (_chart) {
        _chart.destroy()
        _chart = null
    }

    const ctx = document.getElementById('main-chart').getContext('2d')
    const labels = readings.map(r => fmtLabel(r.timestamp))

    const cfgFns = {
        stress: stressConfig,
        climate: climateConfig,
        soil: soilConfig,

        light: lightConfig
    }

    _chart = new Chart(ctx, (cfgFns[tab] || stressConfig)(readings, labels, onPick))
    return _chart

}

function highlightPoint(index) {
    if (!_chart) return

    _chart.data.datasets.forEach(ds => {
        const base = new Array(ds.data.length).fill(3)
        base[index] = 8
        ds.pointRadius = base
    })
    _chart.update('none')

}
