import { describe, it, expect } from 'vitest'
import { render, screen } from '../../test/utils'
import { Header } from '../Header'

describe('Header Component', () => {
  it('renders app title and description', () => {
    render(<Header health="ok" />)
    
    expect(screen.getByText('מערכת הערכת רישוי עסקים')).toBeInTheDocument()
    expect(screen.getByText('מסייעת לבעלי עסקים להבין דרישות רגולטוריות')).toBeInTheDocument()
  })

  it('displays healthy status correctly', () => {
    render(<Header health="ok" />)
    
    expect(screen.getByText('סטטוס מערכת: פעילה')).toBeInTheDocument()
  })

  it('displays unhealthy status correctly', () => {
    render(<Header health="error" />)
    
    expect(screen.getByText('סטטוס מערכת: לא זמינה')).toBeInTheDocument()
  })

  it('displays loading status correctly', () => {
    render(<Header health="loading..." />)
    
    expect(screen.getByText('סטטוס מערכת: לא זמינה')).toBeInTheDocument()
  })

  it('displays unknown status correctly', () => {
    render(<Header health="unknown" />)
    
    expect(screen.getByText('סטטוס מערכת: לא זמינה')).toBeInTheDocument()
  })

  it('applies RTL styling', () => {
    const { container } = render(<Header health="ok" />)
    const headerDiv = container.firstChild as HTMLElement
    
    expect(headerDiv).toHaveStyle({
      textAlign: 'center',
      direction: 'rtl'
    })
  })

  it('has proper color styling for healthy status', () => {
    render(<Header health="ok" />)
    const statusElement = screen.getByText('סטטוס מערכת: פעילה')
    
    expect(statusElement).toHaveStyle({ color: 'rgb(0, 128, 0)' })
  })

  it('has proper color styling for unhealthy status', () => {
    render(<Header health="error" />)
    const statusElement = screen.getByText('סטטוס מערכת: לא זמינה')
    
    expect(statusElement).toHaveStyle({ color: 'rgb(255, 0, 0)' })
  })

  it('renders all text elements with proper styling', () => {
    render(<Header health="ok" />)
    
    const title = screen.getByText('מערכת הערכת רישוי עסקים')
    const subtitle = screen.getByText('מסייעת לבעלי עסקים להבין דרישות רגולטוריות')
    const status = screen.getByText('סטטוס מערכת: פעילה')
    
    expect(title).toHaveStyle({ color: '#333' })
    expect(subtitle).toHaveStyle({ color: '#666' })
    expect(status).toHaveStyle({ fontSize: '12px' })
  })
})
