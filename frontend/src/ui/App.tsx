import React, { useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

export const App: React.FC = () => {
  const [status, setStatus] = useState<string>('loading...')
  const [error, setError] = useState<string>('')

  useEffect(() => {
    const controller = new AbortController()
    fetch(`${API_BASE}/health`, { signal: controller.signal })
    .then(async (res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setError('');           // clear any previous error
      setStatus(data.status || 'unknown');
    })
      .catch((e: any) => {
        if (e.name !== 'AbortError') setError(String(e))
      })
    return () => controller.abort()
  }, [])

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: 24 }}>
      <h1>Licensing Assistant</h1>
      <p>Backend health: {error ? `error: ${error}` : status}</p>
    </div>
  )
}
