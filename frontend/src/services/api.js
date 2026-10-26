export async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, { credentials:'same-origin', ...options, headers:{'X-Requested-With':'RevenueOps', ...(options.body && !(options.body instanceof FormData) ? {'Content-Type':'application/json'} : {}), ...options.headers} })
  const data = response.headers.get('content-type')?.includes('json') ? await response.json() : await response.text()
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Please check the form and try again.')
  return data
}
export const post = (path, body, headers) => api(path,{method:'POST',body:body instanceof FormData ? body : JSON.stringify(body || {}),headers})
export const formatMoney = (value, currency='ZAR') => new Intl.NumberFormat('en-ZA',{style:'currency',currency}).format(value || 0)
