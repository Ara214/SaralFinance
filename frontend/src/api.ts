export type Language = 'english' | 'hindi' | 'hinglish'
export type Sample = { id: string; title: string; message: string }
export type Risk = { risk_level: 'Low' | 'Medium' | 'High'; risk_score: number; risk_reasons: string[]; risk_warning: string | null }
export type Result = Risk & {
  language: Language
  what_happened: string; what_to_do_next: string[]; analogy: string | null
}
const base = (import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '')).replace(/\/$/, '')

export async function request<T>(path: string, body?: object, signal?: AbortSignal): Promise<T> {
  let response: Response
  try {
    response = await fetch(base + path, {
      method: body ? 'POST' : 'GET',
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: signal ? AbortSignal.any([signal, AbortSignal.timeout(25000)]) : AbortSignal.timeout(25000),
    })
  } catch (error) {
    if (signal?.aborted) throw error
    if (error instanceof DOMException && error.name === 'TimeoutError') throw new Error('The request timed out. Try again.')
    throw new Error('Could not connect to SaralFinance. Try again in a moment.')
  }
  if (!response.ok) {
    const error = await response.json().catch(() => null)
    throw new Error(typeof error?.detail === 'string' ? error.detail : 'The request could not be completed. Try again.')
  }
  return response.json() as Promise<T>
}
