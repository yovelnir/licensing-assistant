import { render, screen } from '@testing-library/react'
import { AIReportDisplay } from '../AIReportDisplay'

describe('AIReportDisplay', () => {
  it('should display loading state when loading is true', () => {
    const mockReport = {
      success: false,
      content: '',
      provider: ''
    }

    render(<AIReportDisplay aiReport={mockReport} loading={true} />)
    
    expect(screen.getByText('יוצר דוח חכם באמצעות AI...')).toBeInTheDocument()
    expect(screen.getByText('זה יכול לקחת כמה שניות')).toBeInTheDocument()
    expect(screen.getByText('🤖')).toBeInTheDocument()
  })

  it('should display error state when report is not successful', () => {
    const mockReport = {
      success: false,
      content: '',
      provider: 'test-provider',
      error_message: 'Test error message'
    }

    render(<AIReportDisplay aiReport={mockReport} loading={false} />)
    
    expect(screen.getByText('לא ניתן ליצור דוח AI')).toBeInTheDocument()
    expect(screen.getByText('Test error message')).toBeInTheDocument()
    expect(screen.getByText('ספק AI: test-provider')).toBeInTheDocument()
  })

  it('should display successful report when report is successful', () => {
    const mockReport = {
      success: true,
      content: 'This is a test AI report content',
      provider: 'test-provider',
      model_used: 'gpt-4'
    }

    render(<AIReportDisplay aiReport={mockReport} loading={false} />)
    
    expect(screen.getByText('דוח חכם - AI')).toBeInTheDocument()
    expect(screen.getByText('נוצר באמצעות test-provider (gpt-4)')).toBeInTheDocument()
    expect(screen.getByText('This is a test AI report content')).toBeInTheDocument()
  })

  it('should show loading indicator when report exists but still loading', () => {
    const mockReport = {
      success: true,
      content: 'This is a test AI report content',
      provider: 'test-provider'
    }

    render(<AIReportDisplay aiReport={mockReport} loading={true} />)
    
    // Should show loading state even when report exists
    expect(screen.getByText('יוצר דוח חכם באמצעות AI...')).toBeInTheDocument()
    expect(screen.getByText('זה יכול לקחת כמה שניות')).toBeInTheDocument()
  })
})
