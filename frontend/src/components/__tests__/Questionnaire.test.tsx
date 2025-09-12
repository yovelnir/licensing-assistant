import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '../../test/utils'
import { Questionnaire } from '../Questionnaire'

describe('Questionnaire Component', () => {
  const mockOnChange = vi.fn()
  const mockOnSubmit = vi.fn()

  const defaultProps = {
    questions: [
      {
        name: 'size_m2',
        label: 'גודל העסק (מ"ר)',
        type: 'number',
        required: true,
        min: 1,
        max: 10000,
        placeholder: 'לדוגמה: 150',
        description: 'שטח העסק במטרים מרובעים'
      },
      {
        name: 'seats',
        label: 'מספר מקומות ישיבה / תפוסה',
        type: 'number',
        required: true,
        min: 0,
        max: 1000,
        placeholder: 'לדוגמה: 50',
        description: 'מספר לקוחות שיכולים לשבת במקום'
      },
      {
        name: 'attributes',
        label: 'מאפייני עסק נוספים',
        type: 'multiselect',
        required: false,
        options: [
          { value: 'גז', label: 'שימוש בגז' },
          { value: 'מצלמות', label: 'מצלמות אבטחה' }
        ],
        description: 'בחר את כל המאפיינים הרלוונטיים'
      }
    ],
    answers: {
      size_m2: 150,
      seats: 50,
      attributes: ['גז']
    },
    loading: false,
    isFormValid: true,
    completedRequired: 2,
    requiredFields: ['size_m2', 'seats'],
    validationErrors: [],
    onChange: mockOnChange,
    onSubmit: mockOnSubmit
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Loading State', () => {
    it('shows loading message when no questions provided', () => {
      render(<Questionnaire {...defaultProps} questions={[]} />)
      
      expect(screen.getByText('טוען שאלון...')).toBeInTheDocument()
    })

    it('shows loading message when questions is empty array', () => {
      render(<Questionnaire {...defaultProps} questions={[]} />)
      
      expect(screen.getByText('טוען שאלון...')).toBeInTheDocument()
    })
  })

  describe('Form Rendering', () => {
    it('renders questionnaire title', () => {
      render(<Questionnaire {...defaultProps} />)
      
      expect(screen.getByText('שאלון עסק')).toBeInTheDocument()
    })

    it('renders all questions', () => {
      render(<Questionnaire {...defaultProps} />)
      
      expect(screen.getByText('גודל העסק (מ"ר)')).toBeInTheDocument()
      expect(screen.getByText('מספר מקומות ישיבה / תפוסה')).toBeInTheDocument()
      expect(screen.getByText('מאפייני עסק נוספים')).toBeInTheDocument()
    })

    it('renders instructions', () => {
      render(<Questionnaire {...defaultProps} />)
      
      expect(screen.getByText('הוראות מילוי:')).toBeInTheDocument()
      expect(screen.getByText(/יש למלא את השדות הנדרשים/)).toBeInTheDocument()
    })

    it('renders completion status', () => {
      render(<Questionnaire {...defaultProps} />)
      
      expect(screen.getByText('שדות חובה שהושלמו: 2/2')).toBeInTheDocument()
    })

    it('renders submit button', () => {
      render(<Questionnaire {...defaultProps} />)
      
      const submitButton = screen.getByRole('button', { name: /נתח דרישות רגולטוריות/ })
      expect(submitButton).toBeInTheDocument()
    })
  })

  describe('Form Validation Display', () => {
    it('shows valid form status when form is valid', () => {
      render(<Questionnaire {...defaultProps} isFormValid={true} completedRequired={2} />)
      
      const statusElement = screen.getByText('שדות חובה שהושלמו: 2/2')
      expect(statusElement).toHaveStyle({ color: 'rgb(0, 128, 0)' })
    })

    it('shows invalid form status when form is invalid', () => {
      render(<Questionnaire {...defaultProps} isFormValid={false} completedRequired={1} />)
      
      const statusElement = screen.getByText('שדות חובה שהושלמו: 1/2')
      expect(statusElement).toHaveStyle({ color: '#d68910' })
    })

    it('disables submit button when form is invalid', () => {
      render(<Questionnaire {...defaultProps} isFormValid={false} />)
      
      const submitButton = screen.getByRole('button', { name: /נתח דרישות רגולטוריות/ })
      expect(submitButton).toBeDisabled()
    })

    it('disables submit button when loading', () => {
      render(<Questionnaire {...defaultProps} loading={true} />)
      
      const submitButton = screen.getByRole('button', { name: /מנתח נתונים.../ })
      expect(submitButton).toBeDisabled()
    })

    it('enables submit button when form is valid and not loading', () => {
      render(<Questionnaire {...defaultProps} isFormValid={true} loading={false} />)
      
      const submitButton = screen.getByRole('button', { name: /נתח דרישות רגולטוריות/ })
      expect(submitButton).toBeEnabled()
    })
  })

  describe('Form Submission', () => {
    it('calls onSubmit when form is submitted', () => {
      render(<Questionnaire {...defaultProps} />)
      
      const form = screen.getByRole('form') || screen.getByRole('button', { name: /נתח דרישות רגולטוריות/ }).closest('form')
      fireEvent.submit(form)
      
      expect(mockOnSubmit).toHaveBeenCalledTimes(1)
    })

    it('calls onSubmit with form event', () => {
      render(<Questionnaire {...defaultProps} />)
      
      const form = screen.getByRole('form') || screen.getByRole('button', { name: /נתח דרישות רגולטוריות/ }).closest('form')
      fireEvent.submit(form)
      
      expect(mockOnSubmit).toHaveBeenCalledWith(expect.any(Object))
    })
  })

  describe('Question Rendering', () => {
    it('renders QuestionInput components for each question', () => {
      render(<Questionnaire {...defaultProps} />)
      
      // Check that all question inputs are rendered
      const numberInputs = screen.getAllByRole('spinbutton')
      const checkboxes = screen.getAllByRole('checkbox')
      
      expect(numberInputs).toHaveLength(2) // size_m2 and seats
      expect(checkboxes).toHaveLength(2) // multiselect options
    })

    it('passes correct props to QuestionInput components', () => {
      render(<Questionnaire {...defaultProps} />)
      
      // Check that the first number input has correct attributes
      const firstInput = screen.getAllByRole('spinbutton')[0]
      expect(firstInput).toHaveAttribute('name', 'size_m2')
      expect(firstInput).toHaveAttribute('min', '1')
      expect(firstInput).toHaveAttribute('max', '10000')
    })
  })

  describe('Loading State Button', () => {
    it('shows loading text when loading', () => {
      render(<Questionnaire {...defaultProps} loading={true} />)
      
      expect(screen.getByText('מנתח נתונים...')).toBeInTheDocument()
    })

    it('shows normal text when not loading', () => {
      render(<Questionnaire {...defaultProps} loading={false} />)
      
      expect(screen.getByText('נתח דרישות רגולטוריות')).toBeInTheDocument()
    })
  })

  describe('RTL Styling', () => {
    it('applies RTL styling to container', () => {
      const { container } = render(<Questionnaire {...defaultProps} />)
      const questionnaireDiv = container.firstChild as HTMLElement
      
      expect(questionnaireDiv).toHaveStyle({
        direction: 'rtl',
        textAlign: 'right'
      })
    })

    it('applies RTL styling to title', () => {
      render(<Questionnaire {...defaultProps} />)
      const title = screen.getByText('שאלון עסק')
      
      expect(title).toHaveStyle({
        textAlign: 'right'
      })
    })

    it('applies RTL styling to instructions', () => {
      render(<Questionnaire {...defaultProps} />)
      const instructions = screen.getByText('הוראות מילוי:').parentElement
      
      expect(instructions).toHaveStyle({
        textAlign: 'right',
        direction: 'rtl'
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper form structure', () => {
      render(<Questionnaire {...defaultProps} />)
      
      const form = screen.getByRole('form') || screen.getByRole('button', { name: /נתח דרישות רגולטוריות/ }).closest('form')
      expect(form).toBeInTheDocument()
    })

    it('has proper button accessibility', () => {
      render(<Questionnaire {...defaultProps} />)
      
      const submitButton = screen.getByRole('button', { name: /נתח דרישות רגולטוריות/ })
      expect(submitButton).toHaveAttribute('type', 'submit')
    })
  })

  describe('Edge Cases', () => {
    it('handles empty answers object', () => {
      render(<Questionnaire {...defaultProps} answers={{}} />)
      
      expect(screen.getByText('שאלון עסק')).toBeInTheDocument()
    })

    it('handles null answers', () => {
      render(<Questionnaire {...defaultProps} answers={null as any} />)
      
      expect(screen.getByText('שאלון עסק')).toBeInTheDocument()
    })

    it('handles undefined answers', () => {
      render(<Questionnaire {...defaultProps} answers={undefined as any} />)
      
      expect(screen.getByText('שאלון עסק')).toBeInTheDocument()
    })
  })

  describe('Validation Errors Display', () => {
    it('displays validation errors when present', () => {
      const validationErrors = [
        'גודל העסק חייב להיות בין 1 ל-10,000 מ"ר',
        'מספר מקומות הישיבה חייב להיות בין 0 ל-1,000'
      ]
      
      render(<Questionnaire {...defaultProps} validationErrors={validationErrors} />)
      
      expect(screen.getByText('שגיאות בטופס:')).toBeInTheDocument()
      expect(screen.getByText('גודל העסק חייב להיות בין 1 ל-10,000 מ"ר')).toBeInTheDocument()
      expect(screen.getByText('מספר מקומות הישיבה חייב להיות בין 0 ל-1,000')).toBeInTheDocument()
    })

    it('does not display validation errors when empty', () => {
      render(<Questionnaire {...defaultProps} validationErrors={[]} />)
      
      expect(screen.queryByText('שגיאות בטופס:')).not.toBeInTheDocument()
    })

    it('disables submit button when validation errors present', () => {
      const validationErrors = ['גודל העסק חייב להיות בין 1 ל-10,000 מ"ר']
      
      render(<Questionnaire {...defaultProps} validationErrors={validationErrors} isFormValid={false} />)
      
      const submitButton = screen.getByRole('button', { name: /נתח דרישות רגולטוריות/ })
      expect(submitButton).toBeDisabled()
    })
  })
})
