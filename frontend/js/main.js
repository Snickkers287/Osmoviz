const STRESS_META = {
    heat:{ label: 'Heat',icon: '🔥', css: 'var(--heat)' },
    chilling:{ label: 'Chilling',icon: '❄',  css: 'var(--chilling)' },
    vpd_high:{ label: 'VPD High',icon: '💨', css: 'var(--vpd-high)' },
    vpd_low: { label: 'VPD Low',icon: '🌫', css: 'var(--vpd-low)' },
    light_high:  { label: 'Light High',icon: '☀',  css: 'var(--light-high)' },
    light_low:  { label: 'Light Low',icon: '🌑', css: 'var(--light-low)' },
    waterlogging: { label: 'Waterlogging', icon: '🌊', css: 'var(--waterlogging)' },
    wilting:   { label: 'Wilting', icon: '🍂', css: 'var(--wilting)' }
}

const state = {
    readings : [],
    summary: null,
    index :0,
    tab: 'stress'
}

async function boot(){
    initPlant()
    buildStressBars()
    bindEvents()

     try {
        await api.health()
        setStatus('ok', 'online')
    } catch(e) {
        setStatus('err', 'offline')
    }
    try {
        const scenarios = await api.scenarios()
        populateScenarios(scenarios)
        if (scenarios.length > 0) {
            await loadScenario(scenarios[0].id)
        }
    } catch(e) {
        console.error('boot failed:', e)
    }
}

function populateScenarios(scenarios){
    const sel=document.getElementById('scenario-select')
    sel.innerHTML=scenarios.map(s=>
    `<option value="${s.id}">${s.name} (${s.reading_count} readings)</option>`
    ).join('')
}

async function loadScenario(id){
    try{
        const [readings, summary] = await Promise.all([
            api.readings(id),
            api.summary(id)
        ])
        state.readings = readings
        state.summary = summary
        state.index = 0
        updateSummaryBar(summary)
        document.getElementById('location-chip').textContent = summary.scenario.location || '-'

        initChart(readings,state.tab, i=> showReading(i))
        showReading(0)
    } catch(e) {
        console.error('failed to load scenario', id, e)
    }
}

function  showReading(idx){
    if (!state.readings.length) return
    if (idx<0) idx = 0
    if (idx>=state.readings.length) idx = state.readings.length - 1
    state.index = idx

    const r = state.readings[idx]
    const s = r.stress

    document.getElementById('s-temp').textContent = r.temperature_c.toFixed(1)
    document.getElementById('s-hum').textContent = r.humidity_pct.toFixed(1)
    document.getElementById('s-soil').textContent = r.soil_moisture_pct.toFixed(1)
    document.getElementById('s-lux').textContent = Math.round(r.light_lux).toLocaleString()


    document.getElementById('m-eto').textContent = s.eto_mm_h.toFixed(3)
    document.getElementById('m-etc').textContent = s.etc_mm_h.toFixed(3)
    document.getElementById('m-vpd').textContent = s.vpd_kpa.toFixed(3)

    document.getElementById('score-num').textContent = Math.round(s.overall_stress)


    const tag = document.getElementById('level-tag')
    tag.textContent = s.stress_level.toUpperCase()
    tag.className ='level-tag' + s.stress_level


    const meta = STRESS_META[s.dominant_stress]
    document.getElementById('dominant-tag').textContent=
        meta ? `${meta.icon} ${meta.label}` : s.dominant_stress

    document.getElementById('nav-ts').textContent=fmtTs(r.timestamp)
    document.getElementById('nav-note').textContent = filterNote(r.notes)
    document.getElementById('nav-cnt').textContent = `${idx + 1} / ${state.readings.length}`


    document.getElementById('btn-prev').disabled = idx === 0
    document.getElementById('btn-next').disabled = idx === state.readings.length - 1


    updatePlant(s)
    updateStressBars(s)
    updateRecs(s.recommendations)
    highlightPoint(idx)

}

function filterNote(note){
    if (!note) return ''
    const boring = ['Morning', 'Midday', 'Evening', 'Late night']
    if (boring.includes(note.trim())) return ''
    return note
}

function buildStressBars() {
    const wrap = document.getElementById('stress-bars')
    wrap.innerHTML = Object.entries(STRESS_META).map(([key, m]) => {
        return `
        <div class="srow">
            <div class="srow-lbl">
                <span class="srow-icon">${m.icon}</span>
                <span>${m.label}</span>
            </div>
            <div class="bar-track">
                <div class="bar-fill" id="bar-${key}" style="background:${m.css}; width:0%"></div>
            </div>
            <div class="srow-val" id="bval-${key}">0.000</div>
        </div>`
    }).join('')
}

function updateStressBars(s) {
    const map = {
        heat: s.heat_stress,
        chilling: s.chilling_stress,
        vpd_high: s.vpd_high_stress,
        vpd_low: s.vpd_low_stress,
        light_high: s.light_high_stress,
        light_low: s.light_low_stress,
        waterlogging: s.waterlogging_stress,
        wilting: s.wilting_stress
    }

    Object.entries(map).forEach(([k, v]) => {
        const bar = document.getElementById(`bar-${k}`)
        const val = document.getElementById(`bval-${k}`)
        if (bar) bar.style.width = `${(v * 100).toFixed(1)}%`
        if (val) val.textContent = v.toFixed(3)
    })
}

function updateRecs(recs) {
    const el = document.getElementById('rec-list')
    if (!recs || recs.length === 0) {
        el.innerHTML = '<div class="rec-placeholder">No recommendations</div>'
        return
    }
    el.innerHTML = recs.map(r => `<div class="rec-item">${escHtml(r)}</div>`).join('')
}

function updateSummaryBar(s) {
    document.getElementById('sum-n').textContent = s.total_readings
    document.getElementById('sum-avg').textContent = s.avg_overall_stress.toFixed(1)
    document.getElementById('sum-opt').textContent = `${s.time_in_stress.optimal ?? 0}%`
    document.getElementById('sum-mild').textContent = `${s.time_in_stress.mild ?? 0}%`
    document.getElementById('sum-mod').textContent = `${s.time_in_stress.moderate ?? 0}%`
    document.getElementById('sum-sev').textContent = `${s.time_in_stress.severe ?? 0}%`
    document.getElementById('sum-temp').textContent = `${s.avg_temp.toFixed(1)} °C`
    document.getElementById('sum-vpd').textContent = `${s.avg_vpd.toFixed(3)} kPa`
    document.getElementById('sum-soil').textContent = `${s.min_soil_moisture}–${s.max_soil_moisture} %`
    document.getElementById('sum-eto').textContent = `${s.avg_eto.toFixed(3)} mm/h`
}

function bindEvents() {
    document.getElementById('scenario-select').addEventListener('change', e => {
        loadScenario(parseInt(e.target.value))
    })

    document.getElementById('btn-prev').addEventListener('click', () => {
        showReading(state.index - 1)
    })

    document.getElementById('btn-next').addEventListener('click', () => {
        showReading(state.index + 1)
    })

    document.querySelectorAll('.ctab').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.ctab').forEach(b =>
                b.classList.remove('active'))
            btn.classList.add('active')
            state.tab = btn.dataset.tab
            initChart(state.readings, state.tab, i => showReading(i))
            highlightPoint(state.index)

        })
    })

    document.addEventListener('keydown', e => {
        if (e.key === 'ArrowLeft') showReading(state.index - 1)
        if (e.key === 'ArrowRight') showReading(state.index + 1)
    })
}

function setStatus(cls, text) {
    document.getElementById('status-dot').className = `status-dot ${cls}`
    document.getElementById('status-text').textContent = text

}

function fmtTs(ts) {
    const d = new Date(ts)
    const dy = d.getDate().toString().padStart(2, '0')
    const mo = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getMonth()]
    const hr = d.getHours().toString().padStart(2, '0')
    const mn = d.getMinutes().toString().padStart(2, '0')

    return `${dy} ${mo}  ${hr}:${mn}`
}

function escHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
}


document.addEventListener('DOMContentLoaded', boot)


