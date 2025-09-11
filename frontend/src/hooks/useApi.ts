import { useState, useEffect } from 'react'

const API_BASE = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:5000/api'

// Simple fetch helpers with minimal caching
const cache = new Map<string, any>()

// Export cache clearing function for tests
export const clearCache = () => cache.clear()

export async function get<T>(path: string): Promise<T> {
  const url = `${API_BASE}${path}`
  if (cache.has(url)) return cache.get(url)
  const res = await fetch(url)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  cache.set(url, data)
  return data
}

export async function post<T>(path: string, body: any): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export const useHealthCheck = () => {
  const [health, setHealth] = useState<string>('loading...')

  useEffect(() => {
    const controller = new AbortController()
    fetch(`${API_BASE}/health`, { signal: controller.signal })
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => setHealth(data.status || 'unknown'))
      .catch((e: any) => {
        if (e.name !== 'AbortError') setHealth('error')
      })
    return () => controller.abort()
  }, [])

  return health
}

export const useQuestions = () => {
  const [questions, setQuestions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    get<{ questions: any[] }>(`/questions`)
      .then((data) => {
        setQuestions(data.questions)
        setLoading(false)
      })
      .catch((e) => {
        setError(String(e))
        setLoading(false)
      })
  }, [])

  return { questions, loading, error }
}
