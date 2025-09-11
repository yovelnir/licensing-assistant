import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '../../test/utils'
import { QuestionInput } from '../QuestionInput'

describe('QuestionInput Component', () => {
  const mockOnChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Number Input Type', () => {
    const numberQuestion = {
      name: 'size_m2',
      label: 'גודל העסק (מ"ר)',
      type: 'number',
      required: true,
      min: 1,
      max: 10000,
      placeholder: 'לדוגמה: 150',
      description: 'שטח העסק במטרים מרובעים'
    }

    it('renders number input with correct attributes', () => {
      render(<QuestionInput q={numberQuestion} value={null} onChange={mockOnChange} />)
      
      const input = screen.getByRole('spinbutton')
      expect(input).toBeInTheDocument()
      expect(input).toHaveAttribute('type', 'number')
      expect(input).toHaveAttribute('min', '1')
      expect(input).toHaveAttribute('max', '10000')
      expect(input).toHaveAttribute('placeholder', 'לדוגמה: 150')
      expect(input).toHaveAttribute('required')
    })

    it('displays label with required asterisk', () => {
      render(<QuestionInput q={numberQuestion} value={null} onChange={mockOnChange} />)
      
      expect(screen.getByText('גודל העסק (מ"ר)')).toBeInTheDocument()
      expect(screen.getByText('*')).toBeInTheDocument()
    })

    it('displays description when provided', () => {
      render(<QuestionInput q={numberQuestion} value={null} onChange={mockOnChange} />)
      
      expect(screen.getByText('שטח העסק במטרים מרובעים')).toBeInTheDocument()
    })

    it('calls onChange with number value when input changes', () => {
      render(<QuestionInput q={numberQuestion} value={null} onChange={mockOnChange} />)
      
      const input = screen.getByRole('spinbutton')
      fireEvent.change(input, { target: { value: '150' } })
      
      expect(mockOnChange).toHaveBeenCalledWith('size_m2', 150)
    })

    it('calls onChange with null when input is empty', () => {
      render(<QuestionInput q={numberQuestion} value={150} onChange={mockOnChange} />)
      
      const input = screen.getByRole('spinbutton')
      fireEvent.change(input, { target: { value: '' } })
      
      expect(mockOnChange).toHaveBeenCalledWith('size_m2', null)
    })

    it('applies RTL styling', () => {
      const { container } = render(<QuestionInput q={numberQuestion} value={null} onChange={mockOnChange} />)
      const wrapper = container.firstChild as HTMLElement
      
      expect(wrapper).toHaveStyle({
        direction: 'rtl',
        textAlign: 'right'
      })
    })

    it('applies LTR styling to input field', () => {
      render(<QuestionInput q={numberQuestion} value={null} onChange={mockOnChange} />)
      const input = screen.getByRole('spinbutton')
      
      expect(input).toHaveStyle({
        direction: 'ltr',
        textAlign: 'left'
      })
    })
  })

  describe('Boolean Input Type', () => {
    const booleanQuestion = {
      name: 'uses_gas',
      label: 'שימוש בגז',
      type: 'boolean',
      required: false,
      description: 'האם העסק משתמש בגז'
    }

    it('renders checkbox input', () => {
      render(<QuestionInput q={booleanQuestion} value={false} onChange={mockOnChange} />)
      
      const checkbox = screen.getByRole('checkbox')
      expect(checkbox).toBeInTheDocument()
      expect(checkbox).toHaveAttribute('type', 'checkbox')
    })

    it('displays label without required asterisk when not required', () => {
      render(<QuestionInput q={booleanQuestion} value={false} onChange={mockOnChange} />)
      
      expect(screen.getByText('שימוש בגז')).toBeInTheDocument()
      expect(screen.queryByText('*')).not.toBeInTheDocument()
    })

    it('displays label with required asterisk when required', () => {
      const requiredQuestion = { ...booleanQuestion, required: true }
      render(<QuestionInput q={requiredQuestion} value={false} onChange={mockOnChange} />)
      
      expect(screen.getByText('*')).toBeInTheDocument()
    })

    it('calls onChange with boolean value when checkbox changes', () => {
      render(<QuestionInput q={booleanQuestion} value={false} onChange={mockOnChange} />)
      
      const checkbox = screen.getByRole('checkbox')
      fireEvent.click(checkbox)
      
      expect(mockOnChange).toHaveBeenCalledWith('uses_gas', true)
    })

    it('applies RTL styling with row-reverse flex direction', () => {
      const { container } = render(<QuestionInput q={booleanQuestion} value={false} onChange={mockOnChange} />)
      const wrapper = container.firstChild as HTMLElement
      const label = wrapper.querySelector('label')
      
      expect(wrapper).toHaveStyle({
        direction: 'rtl',
        textAlign: 'right'
      })
      expect(label).toHaveStyle({
        flexDirection: 'row-reverse'
      })
    })
  })

  describe('Multiselect Input Type', () => {
    const multiselectQuestion = {
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

    it('renders all option checkboxes', () => {
      render(<QuestionInput q={multiselectQuestion} value={[]} onChange={mockOnChange} />)
      
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes).toHaveLength(3)
    })

    it('displays all option labels', () => {
      render(<QuestionInput q={multiselectQuestion} value={[]} onChange={mockOnChange} />)
      
      expect(screen.getByText('שימוש בגז')).toBeInTheDocument()
      expect(screen.getByText('מצלמות אבטחה')).toBeInTheDocument()
      expect(screen.getByText('אזור עישון')).toBeInTheDocument()
    })

    it('calls onChange with updated array when option is selected', () => {
      render(<QuestionInput q={multiselectQuestion} value={[]} onChange={mockOnChange} />)
      
      const firstCheckbox = screen.getAllByRole('checkbox')[0]
      fireEvent.click(firstCheckbox)
      
      expect(mockOnChange).toHaveBeenCalledWith('attributes', ['גז'])
    })

    it('calls onChange with updated array when option is deselected', () => {
      render(<QuestionInput q={multiselectQuestion} value={['גז']} onChange={mockOnChange} />)
      
      const firstCheckbox = screen.getAllByRole('checkbox')[0]
      fireEvent.click(firstCheckbox)
      
      expect(mockOnChange).toHaveBeenCalledWith('attributes', [])
    })

    it('handles multiple selections correctly', () => {
      render(<QuestionInput q={multiselectQuestion} value={['גז']} onChange={mockOnChange} />)
      
      const secondCheckbox = screen.getAllByRole('checkbox')[1]
      fireEvent.click(secondCheckbox)
      
      expect(mockOnChange).toHaveBeenCalledWith('attributes', ['גז', 'מצלמות'])
    })

    it('applies RTL styling with row-reverse for checkboxes', () => {
      const { container } = render(<QuestionInput q={multiselectQuestion} value={[]} onChange={mockOnChange} />)
      const wrapper = container.firstChild as HTMLElement
      const labels = wrapper.querySelectorAll('label')
      
      expect(wrapper).toHaveStyle({
        direction: 'rtl',
        textAlign: 'right'
      })
    })
  })

  describe('Edge Cases', () => {
    it('returns null for unknown question type', () => {
      const unknownQuestion = {
        name: 'unknown',
        label: 'Unknown Type',
        type: 'unknown'
      }
      
      const { container } = render(<QuestionInput q={unknownQuestion} value={null} onChange={mockOnChange} />)
      expect(container.firstChild).toBeNull()
    })

    it('handles null value gracefully', () => {
      const numberQuestion = {
        name: 'size_m2',
        label: 'גודל העסק',
        type: 'number',
        required: true
      }
      
      render(<QuestionInput q={numberQuestion} value={null} onChange={mockOnChange} />)
      const input = screen.getByRole('spinbutton')
      expect(input).toHaveValue(null)
    })

    it('handles undefined value gracefully', () => {
      const numberQuestion = {
        name: 'size_m2',
        label: 'גודל העסק',
        type: 'number',
        required: true
      }
      
      render(<QuestionInput q={numberQuestion} value={undefined} onChange={mockOnChange} />)
      const input = screen.getByRole('spinbutton')
      expect(input).toHaveValue(null)
    })
  })
})
