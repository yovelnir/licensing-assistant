import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useForm } from '../useForm'
import { mockApiResponses, mockFetch, resetMocks } from '../../test/utils'

// Mock the useApi module
vi.mock('../useApi', () => ({
  post: vi.fn(),
  useAIAnalysis: vi.fn(() => ({
    analyzeWithAI: vi.fn(),
    generateAIReport: vi.fn(),
    getAIProviders: vi.fn(),
    loading: false,
    error: ''
  }))
}))

describe('useForm Hook', () => {
  const mockQuestions = mockApiResponses.questions.questions
  let mockPost: any

  beforeEach(async () => {
    resetMocks()
    vi.clearAllMocks()
    // Get the mocked post function
    const useApiModule = await import('../useApi')
    mockPost = useApiModule.post
  })

  describe('Initial State', () => {
    it('returns initial state correctly', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      expect(result.current.answers).toEqual({})
      expect(result.current.loading).toBe(false)
      expect(result.current.error).toBe('')
      expect(result.current.result).toBe(null)
      expect(result.current.isFormValid).toBe(false)
      expect(result.current.completedRequired).toBe(0)
      expect(result.current.requiredFields).toEqual(['size_m2', 'seats'])
      expect(result.current.validationErrors).toEqual([
           "גודל העסק (מ\"ר) - שדה חובה",
           "מספר מקומות ישיבה / תפוסה - שדה חובה",
          ])
    })

    it('calculates required fields from questions', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      expect(result.current.requiredFields).toEqual(['size_m2', 'seats'])
    })

    it('handles empty questions array', () => {
      const { result } = renderHook(() => useForm([]))

      expect(result.current.requiredFields).toEqual([])
      expect(result.current.isFormValid).toBe(true)
    })
  })

  describe('onChange Function', () => {
    it('updates answers when onChange is called', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      act(() => {
        result.current.onChange('size_m2', 150)
      })

      expect(result.current.answers).toEqual({ size_m2: 150 })
    })

    it('updates multiple answers', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      act(() => {
        result.current.onChange('size_m2', 150)
        result.current.onChange('seats', 50)
      })

      expect(result.current.answers).toEqual({ size_m2: 150, seats: 50 })
    })

    it('overwrites existing answers', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      act(() => {
        result.current.onChange('size_m2', 150)
        result.current.onChange('size_m2', 200)
      })

      expect(result.current.answers).toEqual({ size_m2: 200 })
    })

    it('handles null values', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      act(() => {
        result.current.onChange('size_m2', 150)
        result.current.onChange('size_m2', null)
      })

      expect(result.current.answers).toEqual({ size_m2: null })
    })
  })

  describe('Form Validation', () => {
    it('calculates form validity correctly', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      // Initially invalid
      expect(result.current.isFormValid).toBe(false)
      expect(result.current.completedRequired).toBe(0)

      // Add one required field
      act(() => {
        result.current.onChange('size_m2', 150)
      })

      expect(result.current.isFormValid).toBe(false)
      expect(result.current.completedRequired).toBe(1)

      // Add second required field
      act(() => {
        result.current.onChange('seats', 50)
      })

      expect(result.current.isFormValid).toBe(true)
      expect(result.current.completedRequired).toBe(2)
    })

    it('handles empty string as invalid', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      act(() => {
        result.current.onChange('size_m2', '')
      })

      expect(result.current.isFormValid).toBe(false)
      expect(result.current.completedRequired).toBe(0)
    })

    it('handles zero as valid for numeric fields', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      act(() => {
        result.current.onChange('size_m2', 0)
        result.current.onChange('seats', 0)
      })

      expect(result.current.isFormValid).toBe(false)
      expect(result.current.completedRequired).toBe(2)
    })

    it('handles undefined as invalid', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      act(() => {
        result.current.onChange('size_m2', undefined)
      })

      expect(result.current.isFormValid).toBe(false)
      expect(result.current.completedRequired).toBe(0)
    })
  })

  describe('onSubmit Function', () => {
    it('prevents default form submission', () => {
      const { result } = renderHook(() => useForm(mockQuestions))
      const mockEvent = {
        preventDefault: vi.fn()
      } as any

      act(() => {
        result.current.onSubmit(mockEvent)
      })

      expect(mockEvent.preventDefault).toHaveBeenCalled()
    })

    it('validates form before submission', async () => {
      const { result } = renderHook(() => useForm(mockQuestions))
      const mockEvent = {
        preventDefault: vi.fn()
      } as any

      // Mock post function to not be called
      mockPost.mockResolvedValue({})

      act(() => {
        result.current.onSubmit(mockEvent)
      })

      // Should not call post because form is invalid
      expect(mockPost).not.toHaveBeenCalled()
      expect(result.current.error).toContain('שגיאות בטופס')
    })

    it('submits form when valid', async () => {
      const { result } = renderHook(() => useForm(mockQuestions))
      const mockEvent = {
        preventDefault: vi.fn()
      } as any

      // Set up valid form
      act(() => {
        result.current.onChange('size_m2', 150)
        result.current.onChange('seats', 50)
      })

      // Mock successful post
      const mockResponse = { success: true }
      mockPost.mockResolvedValue(mockResponse)

      await act(async () => {
        result.current.onSubmit(mockEvent)
      })

      expect(mockPost).toHaveBeenCalledWith('/analyze', { size_m2: 150, seats: 50 })
      expect(result.current.result).toEqual(mockResponse)
      expect(result.current.loading).toBe(false)
    })

    it('handles submission error', async () => {
      const { result } = renderHook(() => useForm(mockQuestions))
      const mockEvent = {
        preventDefault: vi.fn()
      } as any

      // Set up valid form
      act(() => {
        result.current.onChange('size_m2', 150)
        result.current.onChange('seats', 50)
      })

      // Mock post error
      mockPost.mockRejectedValue(new Error('HTTP 500'))

      await act(async () => {
        result.current.onSubmit(mockEvent)
      })

      expect(result.current.error).toBe('שגיאה בשרת - אנא נסה שוב מאוחר יותר')
      expect(result.current.loading).toBe(false)
    })

    it('handles 400 error specifically', async () => {
      const { result } = renderHook(() => useForm(mockQuestions))
      const mockEvent = {
        preventDefault: vi.fn()
      } as any

      // Set up valid form
      act(() => {
        result.current.onChange('size_m2', 150)
        result.current.onChange('seats', 50)
      })

      // Mock 400 error
      mockPost.mockRejectedValue(new Error('HTTP 400'))

      await act(async () => {
        result.current.onSubmit(mockEvent)
      })

      expect(result.current.error).toBe('נתונים לא תקינים - אנא בדוק את השדות החובה')
    })

    it('sets loading state during submission', async () => {
      const { result } = renderHook(() => useForm(mockQuestions))
      const mockEvent = {
        preventDefault: vi.fn()
      } as any

      // Set up valid form
      act(() => {
        result.current.onChange('size_m2', 150)
        result.current.onChange('seats', 50)
      })

      // Mock delayed post
      mockPost.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({}), 100))
      )

      act(() => {
        result.current.onSubmit(mockEvent)
      })

      expect(result.current.loading).toBe(true)

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 150))
      })

      expect(result.current.loading).toBe(false)
    })
  })

  describe('Numeric Validation', () => {
    it('validates size_m2 range', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      act(() => {
        result.current.onChange('size_m2', 0)
        result.current.onChange('seats', 50)
      })

      expect(result.current.isFormValid).toBe(false)

      act(() => {
        result.current.onChange('size_m2', 150)
      })

      expect(result.current.isFormValid).toBe(true)
    })

    it('validates seats range', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      act(() => {
        result.current.onChange('size_m2', 150)
        result.current.onChange('seats', -1)
      })

      expect(result.current.isFormValid).toBe(false)

      act(() => {
        result.current.onChange('seats', 50)
      })

      expect(result.current.isFormValid).toBe(true)
    })

    it('validates maximum values', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      act(() => {
        result.current.onChange('size_m2', 15000)
        result.current.onChange('seats', 50)
      })

      expect(result.current.isFormValid).toBe(false)

      act(() => {
        result.current.onChange('size_m2', 150)
        result.current.onChange('seats', 1500)
      })

      expect(result.current.isFormValid).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('clears error on new submission', async () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      // Set up form with error
      act(() => {
        result.current.onChange('size_m2', 150)
        result.current.onChange('seats', 50)
      })

      mockPost.mockRejectedValue(new Error('HTTP 500'))

      await act(async () => {
        result.current.onSubmit({ preventDefault: vi.fn() } as any)
      })

      expect(result.current.error).toBe('שגיאה בשרת - אנא נסה שוב מאוחר יותר')

      // Clear error and try again
      act(() => {
        result.current.onChange('size_m2', 200)
      })

      expect(result.current.error).toBe('')
    })

    it('handles generic errors', async () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      act(() => {
        result.current.onChange('size_m2', 150)
        result.current.onChange('seats', 50)
      })

      mockPost.mockRejectedValue(new Error('Generic error'))

      await act(async () => {
        result.current.onSubmit({ preventDefault: vi.fn() } as any)
      })

      expect(result.current.error).toBe('שגיאה: Generic error')
    })
  })

  describe('Edge Cases', () => {
    it('handles questions with no required fields', () => {
      const questionsWithoutRequired = mockQuestions.map(q => ({ ...q, required: false }))
      const { result } = renderHook(() => useForm(questionsWithoutRequired))

      expect(result.current.isFormValid).toBe(true)
      expect(result.current.completedRequired).toBe(0)
    })

    it('handles questions with all required fields', () => {
      const allRequiredQuestions = mockQuestions.map(q => ({ ...q, required: true }))
      const { result } = renderHook(() => useForm(allRequiredQuestions))

      expect(result.current.requiredFields).toHaveLength(3)
      expect(result.current.isFormValid).toBe(false)
    })

    it('handles null questions', () => {
      const { result } = renderHook(() => useForm(null as any))

      expect(result.current.requiredFields).toEqual([])
      expect(result.current.isFormValid).toBe(true)
    })
  })

  describe('Validation Errors', () => {
    it('returns validation errors for invalid numeric values', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      act(() => {
        result.current.onChange('size_m2', 15000) // Invalid: exceeds max
        result.current.onChange('seats', 1500) // Invalid: exceeds max
      })

      expect(result.current.validationErrors).toContain('גודל העסק חייב להיות בין 1 ל-10,000 מ"ר')
      expect(result.current.validationErrors).toContain('מספר מקומות הישיבה חייב להיות בין 0 ל-1,000')
      expect(result.current.isFormValid).toBe(false)
    })

    it('clears validation errors when values become valid', () => {
      const { result } = renderHook(() => useForm(mockQuestions))

      // Set invalid values
      act(() => {
        result.current.onChange('size_m2', 15000)
        result.current.onChange('seats', 1500)
      })

      expect(result.current.validationErrors.length).toBeGreaterThan(0)

      // Fix the values
      act(() => {
        result.current.onChange('size_m2', 150)
        result.current.onChange('seats', 50)
      })

      expect(result.current.validationErrors).toEqual([])
      expect(result.current.isFormValid).toBe(true)
    })
  })
})
