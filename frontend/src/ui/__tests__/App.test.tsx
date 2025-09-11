import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '../../test/utils'
import { App } from '../App'
import { mockApiResponses, mockFetch, mockFetchError, resetMocks } from '../../test/utils'
import { useHealthCheck, useQuestions } from '../../hooks/useApi'
import { useForm } from '../../hooks/useForm'

vi.mock('../../hooks/useApi', () => ({
  useHealthCheck: vi.fn(() => 'ok'),
  useQuestions: vi.fn(() => ({
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
    ],
    loading: false,
    error: ''
  }))
}))

vi.mock('../../hooks/useForm', () => ({
  useForm: vi.fn(() => ({
    answers: {},
    loading: false,
    error: '',
    result: null,
    onChange: vi.fn(),
    onSubmit: vi.fn(),
    isFormValid: false,
    completedRequired: 0,
    requiredFields: ['size_m2', 'seats'],
    validationErrors: []
  }))
}))

describe('App Component Integration', () => {
  // Get references to the mocked functions
  const mockUseHealthCheck = vi.mocked(useHealthCheck)
  const mockUseQuestions = vi.mocked(useQuestions)
  const mockUseForm = vi.mocked(useForm)

  beforeEach(() => {
    resetMocks()
    vi.clearAllMocks()
  })

  describe('Basic Rendering', () => {
    it('renders app title and description', () => {
      render(<App />)
      
      expect(screen.getByText('מערכת הערכת רישוי עסקים')).toBeInTheDocument()
      expect(screen.getByText('מסייעת לבעלי עסקים להבין דרישות רגולטוריות')).toBeInTheDocument()
    })

    it('renders questionnaire form', () => {
      render(<App />)
      
      expect(screen.getByText('שאלון עסק')).toBeInTheDocument()
    })

    it('applies RTL styling to main container', () => {
      const { container } = render(<App />)
      const appDiv = container.firstChild as HTMLElement
      
      expect(appDiv).toHaveStyle({
        direction: 'rtl',
        textAlign: 'right'
      })
    })
  })

  describe('Component Integration', () => {
    it('renders all main components', () => {
      render(<App />)
      
      // Header
      expect(screen.getByText('מערכת הערכת רישוי עסקים')).toBeInTheDocument()
      
      // Questionnaire
      expect(screen.getByText('שאלון עסק')).toBeInTheDocument()
      
      // No error display initially
      expect(screen.queryByText('שגיאה:')).not.toBeInTheDocument()
      
      // No results initially
      expect(screen.queryByText('תוצאות הניתוח')).not.toBeInTheDocument()
    })

    it('displays error when questions fail to load', () => {
      mockUseQuestions.mockReturnValue({
        questions: [],
        loading: false,
        error: 'Failed to load questions'
      })

      render(<App />)
      
      expect(screen.getByText('שגיאה:')).toBeInTheDocument()
      expect(screen.getByText('Failed to load questions')).toBeInTheDocument()
    })

    it('displays results when analysis is complete', () => {
      mockUseForm.mockReturnValue({
        answers: { size_m2: 150, seats: 50 },
        loading: false,
        error: '',
        result: mockApiResponses.analyze as any,
        onChange: vi.fn(),
        onSubmit: vi.fn(),
        isFormValid: true,
        completedRequired: 2,
        requiredFields: ['size_m2', 'seats'],
        validationErrors: []
      })

      render(<App />)
      
      expect(screen.getByText('תוצאות הניתוח')).toBeInTheDocument()
    })

    it('displays form error when validation fails', () => {
      mockUseForm.mockReturnValue({
        answers: { size_m2: 150, seats: 50 },
        loading: false,
        error: 'שגיאות בטופס:\nגודל העסק חייב להיות בין 1 ל-10,000 מ"ר',
        result: null,
        onChange: vi.fn(),
        onSubmit: vi.fn(),
        isFormValid: false,
        completedRequired: 1,
        requiredFields: ['size_m2', 'seats'],
        validationErrors: ['גודל העסק חייב להיות בין 1 ל-10,000 מ"ר']
      })

      render(<App />)
      
      expect(screen.getByText('שגיאה:')).toBeInTheDocument()
    })
  })

  describe('Loading States', () => {
    it('shows loading state for questions', () => {
      mockUseQuestions.mockReturnValue({
        questions: [],
        loading: true,
        error: ''
      })

      render(<App />)
      
      expect(screen.getByText('טוען שאלון...')).toBeInTheDocument()
    })

    it('shows loading state for form submission', () => {
      // Mock questions as loaded
      mockUseQuestions.mockReturnValue({
        questions: [
          { name: 'size_m2', label: 'גודל העסק (מ"ר)', type: 'number', required: true },
          { name: 'seats', label: 'מספר מקומות ישיבה', type: 'number', required: true }
        ],
        loading: false,
        error: ''
      })
      
      mockUseForm.mockReturnValue({
        answers: { size_m2: 150, seats: 50 },
        loading: true,
        error: '',
        result: null,
        onChange: vi.fn(),
        onSubmit: vi.fn(),
        isFormValid: true,
        completedRequired: 2,
        requiredFields: ['size_m2', 'seats'],
        validationErrors: []
      })

      render(<App />)
      
      expect(screen.getByText('מנתח נתונים...')).toBeInTheDocument()
    })
  })

  describe('Health Status Integration', () => {
    it('displays healthy status', () => {
      mockUseHealthCheck.mockReturnValue('ok')

      render(<App />)
      
      expect(screen.getByText('סטטוס מערכת: פעילה')).toBeInTheDocument()
    })

    it('displays unhealthy status', () => {
      mockUseHealthCheck.mockReturnValue('error')

      render(<App />)
      
      expect(screen.getByText('סטטוס מערכת: לא זמינה')).toBeInTheDocument()
    })

    it('displays loading status', () => {
      mockUseHealthCheck.mockReturnValue('loading...')

      render(<App />)
      
      expect(screen.getByText('סטטוס מערכת: לא זמינה')).toBeInTheDocument()
    })
  })

  describe('Form Integration', () => {
    it('passes correct props to Questionnaire component', () => {
      const mockOnChange = vi.fn()
      const mockOnSubmit = vi.fn()
      
      // Mock questions as loaded
      mockUseQuestions.mockReturnValue({
        questions: [
          { name: 'size_m2', label: 'גודל העסק (מ"ר)', type: 'number', required: true },
          { name: 'seats', label: 'מספר מקומות ישיבה', type: 'number', required: true }
        ],
        loading: false,
        error: ''
      })
      
      mockUseForm.mockReturnValue({
        answers: { size_m2: 150, seats: 50 },
        loading: false,
        error: '',
        result: null,
        onChange: mockOnChange,
        onSubmit: mockOnSubmit,
        isFormValid: true,
        completedRequired: 2,
        requiredFields: ['size_m2', 'seats'],
        validationErrors: []
      })

      render(<App />)
      
      // Check that form is rendered with correct state
      expect(screen.getByText('שאלון עסק')).toBeInTheDocument()
      expect(screen.getByText('שדות חובה שהושלמו: 2/2')).toBeInTheDocument()
    })

    it('handles form validation errors', () => {
      // Mock questions as loaded
      mockUseQuestions.mockReturnValue({
        questions: [
          { name: 'size_m2', label: 'גודל העסק (מ"ר)', type: 'number', required: true },
          { name: 'seats', label: 'מספר מקומות ישיבה', type: 'number', required: true }
        ],
        loading: false,
        error: ''
      })
      
      mockUseForm.mockReturnValue({
        answers: { size_m2: 15000 }, // Invalid size
        loading: false,
        error: 'שגיאות בטופס:\nגודל העסק חייב להיות בין 1 ל-10,000 מ"ר',
        result: null,
        onChange: vi.fn(),
        onSubmit: vi.fn(),
        isFormValid: false,
        completedRequired: 1,
        requiredFields: ['size_m2', 'seats'],
        validationErrors: ['גודל העסק חייב להיות בין 1 ל-10,000 מ"ר']
      })

      render(<App />)
      
      expect(screen.getByText('שגיאה:')).toBeInTheDocument()
      expect(screen.getByText('שגיאות בטופס:')).toBeInTheDocument()
    })
  })

  describe('Results Integration', () => {
    it('displays results when analysis is complete', () => {
      mockUseForm.mockReturnValue({
        answers: { size_m2: 150, seats: 50, attributes: ['גז'] },
        loading: false,
        error: '',
        result: mockApiResponses.analyze as any,
        onChange: vi.fn(),
        onSubmit: vi.fn(),
        isFormValid: true,
        completedRequired: 2,
        requiredFields: ['size_m2', 'seats'],
        validationErrors: []
      })

      render(<App />)
      
      expect(screen.getByText('תוצאות הניתוח')).toBeInTheDocument()
      expect(screen.getByText('פרופיל העסק')).toBeInTheDocument()
      expect(screen.getByText('סיכום רגולטורי')).toBeInTheDocument()
    })

    it('does not display results when no analysis result', () => {
      mockUseForm.mockReturnValue({
        answers: { size_m2: 150, seats: 50 },
        loading: false,
        error: '',
        result: null,
        onChange: vi.fn(),
        onSubmit: vi.fn(),
        isFormValid: true,
        completedRequired: 2,
        requiredFields: ['size_m2', 'seats'],
        validationErrors: []
      })

      render(<App />)
      
      expect(screen.queryByText('תוצאות הניתוח')).not.toBeInTheDocument()
    })
  })

  describe('Error Handling Integration', () => {
    it('displays both questions error and form error', () => {
      mockUseQuestions.mockReturnValue({
        questions: [],
        loading: false,
        error: 'Failed to load questions'
      })
      
      mockUseForm.mockReturnValue({
        answers: {},
        loading: false,
        error: 'Form validation error',
        result: null,
        onChange: vi.fn(),
        onSubmit: vi.fn(),
        isFormValid: false,
        completedRequired: 0,
        requiredFields: ['size_m2', 'seats'],
        validationErrors: []
      })

      render(<App />)
      
      // Should display the form error (higher priority)
      expect(screen.getByText('שגיאה:')).toBeInTheDocument()
      expect(screen.getByText('Form validation error')).toBeInTheDocument()
    })

    it('prioritizes form error over questions error', () => {
      mockUseQuestions.mockReturnValue({
        questions: [],
        loading: false,
        error: 'Questions error'
      })
      
      mockUseForm.mockReturnValue({
        answers: {},
        loading: false,
        error: 'Form error',
        result: null,
        onChange: vi.fn(),
        onSubmit: vi.fn(),
        isFormValid: false,
        completedRequired: 0,
        requiredFields: ['size_m2', 'seats'],
        validationErrors: []
      })

      render(<App />)
      
      expect(screen.getByText('Form error')).toBeInTheDocument()
      expect(screen.queryByText('Questions error')).not.toBeInTheDocument()
    })
  })

  describe('RTL Integration', () => {
    it('applies RTL styling throughout the app', () => {
      render(<App />)
      
      // Check main container
      const { container } = render(<App />)
      const appDiv = container.firstChild as HTMLElement
      
      expect(appDiv).toHaveStyle({
        direction: 'rtl',
        textAlign: 'right'
      })
    })

    it('maintains RTL styling in all components', () => {
      // Mock questions as loaded to ensure questionnaire renders
      mockUseQuestions.mockReturnValue({
        questions: [
          { name: 'size_m2', label: 'גודל העסק (מ"ר)', type: 'number', required: true },
          { name: 'seats', label: 'מספר מקומות ישיבה', type: 'number', required: true }
        ],
        loading: false,
        error: ''
      })
      
      mockUseForm.mockReturnValue({
        answers: {},
        loading: false,
        error: '',
        result: null,
        onChange: vi.fn(),
        onSubmit: vi.fn(),
        isFormValid: false,
        completedRequired: 0,
        requiredFields: ['size_m2', 'seats'],
        validationErrors: []
      })
      
      render(<App />)
      
      // Header should have RTL
      const header = screen.getByText('מערכת הערכת רישוי עסקים').parentElement
      expect(header).toHaveStyle({ direction: 'rtl' })
      
      // Questionnaire should have RTL
      const questionnaire = screen.getByText('שאלון עסק').parentElement
      expect(questionnaire).toHaveStyle({ direction: 'rtl' })
    })
  })

  describe('Accessibility Integration', () => {
    it('has proper semantic structure', () => {
      // Mock questions as loaded to ensure form renders
      mockUseQuestions.mockReturnValue({
        questions: [
          { name: 'size_m2', label: 'גודל העסק (מ"ר)', type: 'number', required: true },
          { name: 'seats', label: 'מספר מקומות ישיבה', type: 'number', required: true }
        ],
        loading: false,
        error: ''
      })
      
      mockUseForm.mockReturnValue({
        answers: {},
        loading: false,
        error: '',
        result: null,
        onChange: vi.fn(),
        onSubmit: vi.fn(),
        isFormValid: false,
        completedRequired: 0,
        requiredFields: ['size_m2', 'seats'],
        validationErrors: []
      })
      
      render(<App />)
      
      // Should have main heading
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
      
      // Should have form
      expect(screen.getByRole('form')).toBeInTheDocument()
    })

    it('has proper form structure', () => {
      // Mock questions as loaded to ensure form renders
      mockUseQuestions.mockReturnValue({
        questions: [
          { name: 'size_m2', label: 'גודל העסק (מ"ר)', type: 'number', required: true },
          { name: 'seats', label: 'מספר מקומות ישיבה', type: 'number', required: true }
        ],
        loading: false,
        error: ''
      })
      
      mockUseForm.mockReturnValue({
        answers: {},
        loading: false,
        error: '',
        result: null,
        onChange: vi.fn(),
        onSubmit: vi.fn(),
        isFormValid: false,
        completedRequired: 0,
        requiredFields: ['size_m2', 'seats'],
        validationErrors: []
      })
      
      render(<App />)
      
      const form = screen.getByRole('form')
      expect(form).toBeInTheDocument()
      
      // Should have submit button
      const submitButton = screen.getByRole('button', { name: /נתח דרישות רגולטוריות/ })
      expect(submitButton).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('handles empty questions array', () => {
      mockUseQuestions.mockReturnValue({
        questions: [],
        loading: false,
        error: ''
      })

      render(<App />)
      
      expect(screen.getByText('טוען שאלון...')).toBeInTheDocument()
    })

    it('handles null questions', () => {
      mockUseQuestions.mockReturnValue({
        questions: null as any,
        loading: false,
        error: ''
      })

      render(<App />)
      
      expect(screen.getByText('טוען שאלון...')).toBeInTheDocument()
    })

    it('handles undefined questions', () => {
      mockUseQuestions.mockReturnValue({
        questions: undefined as any,
        loading: false,
        error: ''
      })

      render(<App />)
      
      expect(screen.getByText('טוען שאלון...')).toBeInTheDocument()
    })
  })
})