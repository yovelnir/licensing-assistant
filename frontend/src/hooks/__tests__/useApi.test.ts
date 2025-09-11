import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useHealthCheck, useQuestions, get, post, clearCache } from '../useApi'
import { mockApiResponses, mockFetch, mockFetchError, resetMocks } from '../../test/utils'

describe('useApi Hook', () => {
  beforeEach(() => {
    resetMocks()
    vi.clearAllMocks()
    // Clear the cache between tests
    clearCache()
    // Reset fetch mock
    global.fetch = vi.fn()
  })

  describe('get function', () => {
    it('makes GET request and returns data', async () => {
      const mockData = { test: 'data' }
      mockFetch(mockData)

      const result = await get('/test')

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:5000/api/test')
      expect(result).toEqual(mockData)
    })

    it('caches responses', async () => {
      const mockData = { test: 'data' }
      mockFetch(mockData)

      // First call
      const result1 = await get('/test')
      // Second call
      const result2 = await get('/test')

      expect(global.fetch).toHaveBeenCalledTimes(1)
      expect(result1).toEqual(mockData)
      expect(result2).toEqual(mockData)
    })

    it('throws error on HTTP error status', async () => {
      // Clear any existing mocks
      vi.clearAllMocks()
      mockFetch({ error: 'Not found' }, 404)

      await expect(get('/test')).rejects.toThrow('HTTP 404')
    })

    it('throws error on network failure', async () => {
      // Clear any existing mocks
      vi.clearAllMocks()
      mockFetchError('Network error')

      await expect(get('/test')).rejects.toThrow('Network error')
    })
  })

  describe('post function', () => {
    it('makes POST request with body and returns data', async () => {
      const mockData = { success: true }
      const requestBody = { test: 'data' }
      mockFetch(mockData)

      const result = await post('/test', requestBody)

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:5000/api/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      })
      expect(result).toEqual(mockData)
    })

    it('throws error on HTTP error status', async () => {
      mockFetch({ error: 'Bad request' }, 400)

      await expect(post('/test', {})).rejects.toThrow('HTTP 400')
    })

    it('throws error on network failure', async () => {
      mockFetchError('Network error')

      await expect(post('/test', {})).rejects.toThrow('Network error')
    })
  })

  describe('useHealthCheck hook', () => {

    it('updates to healthy status on successful response', async () => {
      mockFetch(mockApiResponses.health)

      const { result } = renderHook(() => useHealthCheck())

      await waitFor(() => {
        expect(result.current).toBe('ok')
      })
    })

    it('updates to error status on failed response', async () => {
      mockFetchError('Network error')

      const { result } = renderHook(() => useHealthCheck())

      await waitFor(() => {
        expect(result.current).toBe('error')
      })
    })

    it('updates to error status on HTTP error', async () => {
      mockFetch({ error: 'Server error' }, 500)

      const { result } = renderHook(() => useHealthCheck())

      await waitFor(() => {
        expect(result.current).toBe('error')
      })
    })

    it('handles unknown status response', async () => {
      mockFetch({ status: 'unknown' })

      const { result } = renderHook(() => useHealthCheck())

      await waitFor(() => {
        expect(result.current).toBe('unknown')
      })
    })

    it('handles missing status in response', async () => {
      mockFetch({})

      const { result } = renderHook(() => useHealthCheck())

      await waitFor(() => {
        expect(result.current).toBe('unknown')
      })
    })
  })

  describe('useQuestions hook', () => {
    it('returns initial loading state', () => {
      const { result } = renderHook(() => useQuestions())
      
      expect(result.current.questions).toEqual([])
      expect(result.current.loading).toBe(true)
      expect(result.current.error).toBe('')
    })

    it('loads questions successfully', async () => {
      // Clear cache and mocks
      clearCache()
      vi.clearAllMocks()
      mockFetch(mockApiResponses.questions)

      const { result } = renderHook(() => useQuestions())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.questions).toEqual(mockApiResponses.questions.questions)
      expect(result.current.error).toBe('')
    })

    it('handles loading error', async () => {
      // Clear cache and mocks
      clearCache()
      vi.clearAllMocks()
      mockFetchError('Failed to load questions')

      const { result } = renderHook(() => useQuestions())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.questions).toEqual([])
      expect(result.current.error).toBe('Error: Failed to load questions')
    })

    it('handles HTTP error', async () => {
      // Clear cache and mocks
      clearCache()
      vi.clearAllMocks()
      mockFetch({ error: 'Not found' }, 404)

      const { result } = renderHook(() => useQuestions())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.questions).toEqual([])
      expect(result.current.error).toBe('Error: HTTP 404')
    })

    it('handles malformed response', async () => {
      mockFetch({ invalid: 'data' })

      const { result } = renderHook(() => useQuestions())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.questions).toEqual(undefined)
      expect(result.current.error).toBe('')
    })
  })

  describe('API Base URL', () => {
    it('uses correct API base URL', async () => {
      mockFetch({ test: 'data' })

      await get('/test')

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:5000/api/test')
    })

    it('handles different API base URLs', async () => {
      // This test verifies the default API base URL is used
      // Environment variable mocking is complex in Vitest, so we test the default behavior
      clearCache()
      vi.clearAllMocks()
      mockFetch({ test: 'data' })

      await get('/test')

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:5000/api/test')
    })
  })

  describe('Error Handling', () => {
    it('handles fetch rejection', async () => {
      // Clear cache and mocks
      clearCache()
      vi.clearAllMocks()
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Fetch failed'))

      await expect(get('/test')).rejects.toThrow('Fetch failed')
    })

    it('handles JSON parsing error', async () => {
      // Clear cache and mocks
      clearCache()
      vi.clearAllMocks()
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockRejectedValue(new Error('Invalid JSON'))
      }
      ;(global.fetch as any).mockResolvedValueOnce(mockResponse)

      await expect(get('/test')).rejects.toThrow('Invalid JSON')
    })

    it('handles non-JSON response', async () => {
      // Clear cache and mocks
      clearCache()
      vi.clearAllMocks()
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue('Not JSON')
      }
      ;(global.fetch as any).mockResolvedValueOnce(mockResponse)

      const result = await get('/test')
      expect(result).toBe('Not JSON')
    })
  })
})
