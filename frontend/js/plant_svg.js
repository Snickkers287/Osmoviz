const PLANT_SVG = `
<svg viewBox="0 0 200 280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="soilGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#3d2b1a"/>
      <stop offset="100%" stop-color="#180e06"/>
    </linearGradient>
    <radialGradient id="fruit1Grad" cx="35%" cy="30%" r="65%">
      <stop offset="0%" stop-color="#e74c3c"/>
      <stop offset="100%" stop-color="#922b21"/>
    </radialGradient>
    <radialGradient id="fruit2Grad" cx="35%" cy="30%" r="65%">
        <stop offset="0%" stop-color="#e74c3c"/>
        <stop offset="100%" stop-color="#922b21"/>
    </radialGradient>
    <radialGradient id="fruit3Grad" cx="35%" cy="30%" r="65%">
      <stop offset="0%" stop-color="#cd4030"/>
      <stop offset="100%" stop-color="#7b241c"/>
    </radialGradient>
  </defs>

  <rect x="8" y="218" width="184" height="62" rx="7" fill="url(#soilGrad)"/>
  <ellipse cx="100" cy="218" rx="92" ry="9" fill="#4a3520"/>
  <ellipse cx="100" cy="218" rx="76" ry="5.5" fill="#3a2a18"/>

  <g id="roots" class="plant-part">
    <path d="M100,217 Q99,236 97,254" stroke="#6b4226" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <path d="M99,231 Q83,240 65,252" stroke="#6b4226" stroke-width="2" fill="none" stroke-linecap="round"/>
    <path d="M101,231 Q117,240 135,252" stroke="#6b4226" stroke-width="2" fill="none" stroke-linecap="round"/>
    <path d="M97,245 Q78,255 60,265" stroke="#5a3820" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    <path d="M103,245 Q122,255 140,265" stroke="#5a3820" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    <path d="M96,256 Q80,264 66,272" stroke="#4a2e18" stroke-width="1" fill="none" stroke-linecap="round"/>
    <path d="M104,256 Q120,264 134,272" stroke="#4a2e18" stroke-width="1" fill="none" stroke-linecap="round"/>
  </g>

  <g id="stem" class="plant-part">
    <path id="stem-path" d="M100,217 Q97,190 99,160 Q101,125 99,96 Q100,74 100,52"
      stroke="#2d6a2d" stroke-width="5.5" fill="none" stroke-linecap="round"/>
    <path d="M101,217 Q98,190 100,160 Q102,125 100,96 Q101,74 101,52"
      stroke="rgba(255,255,255,0.06)" stroke-width="2" fill="none" stroke-linecap="round"/>
  </g>

  <g id="leaves-lower" class="plant-part leaves">
    <path id="leaf-ll" d="M99,186 Q72,170 48,181 Q56,199 99,186" fill="#2d8a2d"/>
    <path id="leaf-lr" d="M101,186 Q128,170 152,181 Q144,199 101,186" fill="#2d8a2d"/>
    <path d="M99,186 Q72,178 48,181" stroke="rgba(0,0,0,0.18)" stroke-width="0.9" fill="none"/>
    <path d="M101,186 Q128,178 152,181" stroke="rgba(0,0,0,0.18)" stroke-width="0.9" fill="none"/>
  </g>

  <g id="leaves-mid" class="plant-part leaves">
      <path id="leaf-ml" d="M99,147 Q69,131 44,142 Q54,161 99,147" fill="#339933"/>
      <path id="leaf-mr" d="M101,147 Q131,131 156,142 Q146,161 101,147" fill="#339933"/>
      <path d="M99,147 Q69,139 44,142" stroke="rgba(0,0,0,0.18)" stroke-width="0.9" fill="none"/>
      <path d="M101,147 Q131,139 156,142" stroke="rgba(0,0,0,0.18)" stroke-width="0.9" fill="none"/>
  </g>

  <g id="leaves-upper" class="plant-part leaves">
    <path id="leaf-ul" d="M99,103 Q76,88 56,96 Q66,114 99,103" fill="#3aaa3a"/>
    <path id="leaf-ur" d="M101,103 Q124,88 144,96 Q134,114 101,103" fill="#3aaa3a"/>
    <path d="M99,103 Q76,96 56,96" stroke="rgba(0,0,0,0.18)" stroke-width="0.9" fill="none"/>
    <path d="M101,103 Q124,96 144,96" stroke="rgba(0,0,0,0.18)" stroke-width="0.9" fill="none"/>
  </g>
  <path d="M100,80 Q87,74 76,79" stroke="#2d6a2d" stroke-width="1.5" fill="none"/>
  <path d="M100,80 Q112,73 122,78" stroke="#2d6a2d" stroke-width="1.5" fill="none"/>
  <path d="M100,80 Q100,67 100,61" stroke="#2d6a2d" stroke-width="1.5" fill="none"/>

  <g id="fruits" class="plant-part">
    <circle id="fruit-1" cx="73" cy="84" r="12" fill="url(#fruit1Grad)"/>
    <ellipse cx="69" cy="79" rx="5" ry="3.5" fill="rgba(255,255,255,0.14)" transform="rotate(-20,69,79)"/>

    <circle id="fruit-2" cx="126" cy="82" r="11" fill="url(#fruit2Grad)"/>
    <ellipse cx="122" cy="77" rx="4.5" ry="3" fill="rgba(255,255,255,0.14)" transform="rotate(-20,122,77)"/>

    <circle id="fruit-3" cx="100" cy="57" r="10" fill="url(#fruit3Grad)"/>
    <ellipse cx="96" cy="52" rx="4" ry="2.5" fill="rgba(255,255,255,0.14)" transform="rotate(-20,96,52)"/>
    <path d="M73,72 Q70,68 73,66 Q76,68 73,72" fill="#2d6a2d"/>
    <path d="M126,71 Q123,67 126,65 Q129,67 126,71" fill="#2d6a2d"/>
    <path d="M100,47 Q97,43 100,41 Q103,43 100,47" fill="#2d6a2d"/>
  </g>

  <g id="growing-tip">
    <path d="M100,52 Q97,44 100,40 Q103,44 100,52" fill="#4aaa4a"/>
    <path d="M100,47 Q93,41 89,37" stroke="#4aaa4a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    <path d="M100,47 Q107,41 111,37" stroke="#4aaa4a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  </g>
</svg>`;
const STRESS_LEAF_COLOR = {
    heat: '#fb923c',
    chilling: '#93c5fd',
    vpd_high: '#fed7aa',
    vpd_low: '#d1d5db',
    light_high: '#fde68a',
    light_low: '#d4f1a4',
    waterlogging: '#86efac',
    wilting: '#9ca3af',
    optimal: null
}

const STRESS_STEM_COLOR = {
    heat: '#3d8a2d',
    chilling: '#3a5ca0',
    vpd_high: '#3d8a2d',
    vpd_low: '#3d8a2d',
    light_high: '#3d8a2d',
    light_low: '#5a8a2a',
    waterlogging: '#3d8a2d',
    wilting: '#5a7050',
    optimal: '#2d6a2d'
}

const STRESS_ROOT_COLOR = {
    waterlogging: '#92400e',
    wilting: '#8b4513',
    optimal: '#6b4226'
}
const DEFAULT_LEAVES = {
    'leaf-ll': '#2d8a2d',
    'leaf-lr': '#2d8a2d',
    'leaf-ml': '#339933',
    'leaf-mr': '#339933',
    'leaf-ul': '#3aaa3a',
    'leaf-ur': '#3aaa3a'
}

const DEFAULT_STEM = '#2d6a2d'
const DEFAULT_ROOTS = '#6b4226'

function initPlant() {
    document.getElementById('plant-wrap').innerHTML = PLANT_SVG
}

function updatePlant(stress) {
    const svg = document.querySelector('#plant-wrap svg')
    if (!svg) return

    const dom = stress.dominant_stress
    const lvl = stress.stress_level
    const act = stress.active_stresses || []

    const leafColor = STRESS_LEAF_COLOR[dom] || null
    const leafIds = ['leaf-ll', 'leaf-lr', 'leaf-ml', 'leaf-mr', 'leaf-ul', 'leaf-ur']
    leafIds.forEach(id => {
        const el = svg.getElementById(id)
        if (!el) return
        el.style.fill = leafColor || DEFAULT_LEAVES[id]
    })

    const stemEl = svg.getElementById('stem-path')
    if (stemEl) stemEl.style.stroke = STRESS_STEM_COLOR[dom] || DEFAULT_STEM

    const rootColor = STRESS_ROOT_COLOR[dom] || DEFAULT_ROOTS
    svg.querySelectorAll('#roots path').forEach(p => {
        p.style.stroke = rootColor
    })

    const shouldPulse = lvl === 'moderate' || lvl === 'severe'
    ;['leaves-lower', 'leaves-mid', 'leaves-upper'].forEach(id => {
        const el = svg.getElementById(id)
        if (el) el.classList.toggle('stressed-leaves', shouldPulse)
    })

    const rootsEl = svg.getElementById('roots')
    if (rootsEl) rootsEl.classList.toggle('stressed-roots', act.includes('waterlogging'))
    const scoreEl = document.getElementById('score-num')
    if (scoreEl) {
        const colors = {
            optimal: 'var(--optimal)',
            mild: 'var(--mild)',
            moderate: 'var(--moderate)',
            severe: 'var(--severe)'
        }
        scoreEl.style.color = colors[lvl] || 'var(--text2)'
    }
}