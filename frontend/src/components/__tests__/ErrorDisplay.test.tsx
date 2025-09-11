import { describe, it, expect } from 'vitest'
import { render, screen } from '../../test/utils'
import { ErrorDisplay } from '../ErrorDisplay'

describe('ErrorDisplay Component', () => {
  it('renders nothing when no error is provided', () => {
    const { container } = render(<ErrorDisplay error="" />)
    
    expect(container.firstChild).toBeNull()
  })

  it('renders nothing when error is null', () => {
    const { container } = render(<ErrorDisplay error={null as any} />)
    
    expect(container.firstChild).toBeNull()
  })

  it('renders nothing when error is undefined', () => {
    const { container } = render(<ErrorDisplay error={undefined as any} />)
    
    expect(container.firstChild).toBeNull()
  })

  it('renders error message when error is provided', () => {
    const errorMessage = 'שגיאה בטופס'
    render(<ErrorDisplay error={errorMessage} />)
    
    expect(screen.getByText('שגיאה:')).toBeInTheDocument()
    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it('applies proper RTL styling', () => {
    render(<ErrorDisplay error="שגיאה בטופס" />)
    const errorElement = screen.getByText('שגיאה:').parentElement
    
    expect(errorElement).toHaveStyle({
      direction: 'rtl',
      textAlign: 'right'
    })
  })

  it('applies error styling', () => {
    render(<ErrorDisplay error="שגיאה בטופס" />)
    const errorElement = screen.getByText('שגיאה:').parentElement
    
    expect(errorElement).toHaveStyle({
      backgroundColor: '#fee',
      border: '1px solid #f88',
      borderRadius: '4px',
      padding: '16px',
      marginBottom: '24px'
    })
  })

  it('applies proper text styling', () => {
    render(<ErrorDisplay error="שגיאה בטופס" />)
    const errorLabel = screen.getByText('שגיאה:')
    
    expect(errorLabel).toHaveStyle({
      color: '#d00'
    })
  })

  it('handles special characters in error messages', () => {
    const specialError = 'שגיאה עם תווים מיוחדים: !@#$%^&*()_+-=[]{}|;:,.<>?'
    render(<ErrorDisplay error={specialError} />)
    
    expect(screen.getByText('שגיאה:')).toBeInTheDocument()
    expect(screen.getByText(specialError)).toBeInTheDocument()
  })
})
