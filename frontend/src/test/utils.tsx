import React, { ReactElement } from 'react'
import { render, RenderOptions, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

// Mock API responses
export const mockApiResponses = {
  health: { status: 'ok' },
  questions: {
    questions: [
      {
        name: 'size_m2',
        label: 'גודל העסק (מ"ר)',
        type: 'number',
        required: true,
        min: 1,
        max: 10000,
        placeholder: 'לדוגמה: 150',
        description: 'שטח העסק במטרים מרובעים - נדרש לצורך סינון דרישות'
      },
      {
        name: 'seats',
        label: 'מספר מקומות ישיבה / תפוסה',
        type: 'number',
        required: true,
        min: 0,
        max: 1000,
        placeholder: 'לדוגמה: 50',
        description: 'מספר לקוחות שיכולים לשבת במקום - נדרש לצורך סינון דרישות'
      },
      {
        name: 'attributes',
        label: 'מאפייני עסק נוספים',
        type: 'multiselect',
        required: false,
        options: [
          { value: 'גז', label: 'שימוש בגז' },
          { value: 'מצלמות', label: 'מצלמות אבטחה' },
          { value: 'עישון', label: 'אזור עישון' }
        ],
        description: 'בחר את כל המאפיינים הרלוונטיים'
      }
    ]
  },
  analyze: {
    user_input: {
      size_m2: 150,
      seats: 50,
      attributes: ['גז']
    },
    business_analysis: {
      profile: { size_m2: 150, seats: 50, attributes: ['גז'] },
      classification: {
        size_category: 'small',
        occupancy_category: 'low'
      },
      risk_factors: ['גז']
    },
    regulatory_analysis: {
      matched_requirements: [
        {
          paragraph_number: '4.2.1',
          text: 'דרישה לגז במטבח',
          priority: 'high',
          category: 'בטיחות'
        }
      ],
      by_category: {
        'בטיחות': [
          {
            paragraph_number: '4.2.1',
            text: 'דרישה לגז במטבח',
            priority: 'high'
          }
        ]
      },
      total_matches: 1,
      priority_breakdown: { high: 1, medium: 0, low: 0 },
      avg_relevance: 0.85
    },
    feature_coverage: { 'גז': 1 },
    recommendations: {
      immediate_actions: ['התקן מערכת גז בטוחה'],
      estimated_complexity: 'medium'
    },
    analysis_metadata: {
      timestamp: '2024-01-01T00:00:00Z',
      version: '1.0'
    }
  }
}

// Custom render function with providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

// Mock fetch responses
export const mockFetch = (response: any, status = 200) => {
  const mockResponse = {
    ok: status >= 200 && status < 300,
    status,
    json: vi.fn().mockResolvedValue(response)
  }
  ;(global.fetch as any).mockResolvedValue(mockResponse)
  return mockResponse
}

// Mock fetch error
export const mockFetchError = (message = 'Network error') => {
  ;(global.fetch as any).mockRejectedValue(new Error(message))
}

// Reset mocks
export const resetMocks = () => {
  vi.clearAllMocks()
  ;(global.fetch as any).mockClear()
}

// Test data factories
export const createQuestion = (overrides = {}) => ({
  name: 'test_question',
  label: 'Test Question',
  type: 'text',
  required: false,
  ...overrides
})

export const createUserInput = (overrides = {}) => ({
  size_m2: 100,
  seats: 25,
  attributes: [],
  ...overrides
})

export const createAnalysisResult = (overrides = {}) => ({
  user_input: createUserInput(),
  business_analysis: {
    profile: createUserInput(),
    classification: { size_category: 'small', occupancy_category: 'low' },
    risk_factors: []
  },
  regulatory_analysis: {
    matched_requirements: [],
    by_category: {},
    total_matches: 0,
    priority_breakdown: { high: 0, medium: 0, low: 0 },
    avg_relevance: 0
  },
  feature_coverage: {},
  recommendations: { immediate_actions: [], estimated_complexity: 'low' },
  analysis_metadata: { timestamp: '2024-01-01T00:00:00Z', version: '1.0' },
  ...overrides
})

// Re-export everything
export { customRender as render }
export { screen, fireEvent, waitFor }
