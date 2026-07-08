const BASE = '/api';

async function apiFetch(path, options = {}){
    const r = await fetch(`${BASE}${path}`,options);
    return r.json();
}

const api = {
    health: () => apiFetch('/health'),
    scenarios: () => apiFetch('/scenarios'),
    readings:(id) => apiFetch(`/scenarios/${id}/readings`),
    summary:(id)=> apiFetch(`/scenarios/${id}/summary`),
    compute:   (body) => apiFetch('/compute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    }),
};