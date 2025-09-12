import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '../../test/utils'
import { ResultsDisplay } from '../ResultsDisplay'
import { createAnalysisResult } from '../../test/utils'

describe('ResultsDisplay Component', () => {
  const mockResult = createAnalysisResult({
    user_input: {
      size_m2: 150,
      seats: 50,
      attributes: ['גז', 'מצלמות']
    },
    business_analysis: {
      profile: { size_m2: 150, seats: 50, attributes: ['גז', 'מצלמות'] },
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
          text: 'דרישה לגז במטבח - יש להתקין מערכת גז בטוחה',
          priority: 'high',
          category: 'בטיחות'
        },
        {
          paragraph_number: '4.2.2',
          text: 'דרישה למצלמות אבטחה - יש להתקין מערכת מצלמות',
          priority: 'medium',
          category: 'אבטחה'
        }
      ],
      by_category: {
        'בטיחות': [
          {
            paragraph_number: '4.2.1',
            text: 'דרישה לגז במטבח - יש להתקין מערכת גז בטוחה',
            priority: 'high'
          }
        ],
        'אבטחה': [
          {
            paragraph_number: '4.2.2',
            text: 'דרישה למצלמות אבטחה - יש להתקין מערכת מצלמות',
            priority: 'medium'
          }
        ]
      },
      total_matches: 2,
      priority_breakdown: { high: 1, medium: 1, low: 0 },
      avg_relevance: 0.85
    },
    feature_coverage: { 'גז': 1, 'מצלמות': 1 },
    recommendations: {
      immediate_actions: [
        'התקן מערכת גז בטוחה',
        'התקן מערכת מצלמות אבטחה'
      ],
      estimated_complexity: 'high'
    }
  })

  describe('Basic Rendering', () => {
    it('renders results title', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      expect(screen.getByText('תוצאות הניתוח')).toBeInTheDocument()
    })

    it('applies RTL styling to container', () => {
      const { container } = render(<ResultsDisplay result={mockResult} />)
      const resultsDiv = container.firstChild as HTMLElement
      
      expect(resultsDiv).toHaveStyle({
        direction: 'rtl',
        textAlign: 'right'
      })
    })
  })

  describe('Business Profile Section', () => {
    it('renders business profile title', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      expect(screen.getByText('פרופיל העסק')).toBeInTheDocument()
    })

    it('displays additional attributes when present', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      expect(screen.getByText('מאפיינים נוספים:')).toBeInTheDocument()
      expect(screen.getByText('גז, מצלמות')).toBeInTheDocument()
    })

    it('does not display additional attributes when empty', () => {
      const resultWithoutAttributes = {
        ...mockResult,
        user_input: { ...mockResult.user_input, attributes: [] }
      }
      render(<ResultsDisplay result={resultWithoutAttributes} />)
      
      expect(screen.queryByText('מאפיינים נוספים:')).not.toBeInTheDocument()
    })

    it('handles missing business analysis gracefully', () => {
      const resultWithoutAnalysis = {
        ...mockResult,
        business_analysis: {}
      }
      render(<ResultsDisplay result={resultWithoutAnalysis} />)
      
      expect(screen.getByText('פרופיל העסק')).toBeInTheDocument()
    })
  })

  describe('Regulatory Summary Section', () => {
    it('renders regulatory summary title', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      expect(screen.getByText('סיכום רגולטורי')).toBeInTheDocument()
    })

    it('displays total requirements count', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      expect(screen.getByText('סה"כ דרישות:')).toBeInTheDocument()
      expect(screen.getByText('2')).toBeInTheDocument()
    })

    it('displays priority breakdown', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      expect(screen.getByText('עדיפות גבוהה:')).toBeInTheDocument()
      expect(screen.getAllByText('1')).toHaveLength(2) // Both high and medium priority show "1"
      expect(screen.getByText('עדיפות בינונית:')).toBeInTheDocument()
    })

    it('displays complexity information', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      expect(screen.getByText('מורכבות:')).toBeInTheDocument()
      expect(screen.getByText('גבוהה')).toBeInTheDocument()
    })

    it('handles missing regulatory analysis gracefully', () => {
      const resultWithoutAnalysis = {
        ...mockResult,
        regulatory_analysis: {}
      }
      render(<ResultsDisplay result={resultWithoutAnalysis} />)
      
      expect(screen.getByText('סיכום רגולטורי')).toBeInTheDocument()
    })
  })

  describe('Categories Section', () => {
    it('renders categories when present', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      expect(screen.getByText('דרישות לפי קטגוריה')).toBeInTheDocument()
      expect(screen.getByText('בטיחות (1 דרישות)')).toBeInTheDocument()
      expect(screen.getByText('אבטחה (1 דרישות)')).toBeInTheDocument()
    })

    it('does not render categories section when empty', () => {
      const resultWithoutCategories = {
        ...mockResult,
        regulatory_analysis: {
          ...mockResult.regulatory_analysis,
          by_category: {}
        }
      }
      render(<ResultsDisplay result={resultWithoutCategories} />)
      
      expect(screen.queryByText('דרישות לפי קטגוריה')).not.toBeInTheDocument()
    })

    it('renders collapsible category details', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      const safetyCategory = screen.getByText('בטיחות (1 דרישות)')
      expect(safetyCategory).toBeInTheDocument()
      
      // Check that details element exists
      const detailsElement = safetyCategory.closest('details')
      expect(detailsElement).toBeInTheDocument()
    })

    it('displays requirement details when category is expanded', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      const safetyCategory = screen.getByText('בטיחות (1 דרישות)')
      const detailsElement = safetyCategory.closest('details')
      
      // Open the details
      fireEvent.click(safetyCategory)
      
      expect(screen.getByText('סעיף 4.2.1')).toBeInTheDocument()
      expect(screen.getByText(/דרישה לגז במטבח/)).toBeInTheDocument()
    })

    it('displays priority badges correctly', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      const safetyCategory = screen.getByText('בטיחות (1 דרישות)')
      fireEvent.click(safetyCategory)
      
      expect(screen.getByText('עדיפות גבוהה')).toBeInTheDocument()
    })

    it('limits displayed requirements to 3 per category', () => {
      const resultWithManyRequirements = {
        ...mockResult,
        regulatory_analysis: {
          ...mockResult.regulatory_analysis,
          by_category: {
            'בטיחות': Array.from({ length: 5 }, (_, i) => ({
              paragraph_number: `4.2.${i + 1}`,
              text: `דרישה ${i + 1}`,
              priority: 'high'
            }))
          }
        }
      }
      
      render(<ResultsDisplay result={resultWithManyRequirements} />)
      
      const safetyCategory = screen.getByText('בטיחות (5 דרישות)')
      fireEvent.click(safetyCategory)
      
      // Should show first 3 requirements
      expect(screen.getByText('סעיף 4.2.1')).toBeInTheDocument()
      expect(screen.getByText('סעיף 4.2.2')).toBeInTheDocument()
      expect(screen.getByText('סעיף 4.2.3')).toBeInTheDocument()
      
      // Should show "and more" message
      expect(screen.getByText('ועוד 2 דרישות נוספות...')).toBeInTheDocument()
    })
  })

  describe('Recommendations Section', () => {
    it('renders recommendations when present', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      expect(screen.getByText('המלצות לפעולה')).toBeInTheDocument()
      expect(screen.getByText('התקן מערכת גז בטוחה')).toBeInTheDocument()
      expect(screen.getByText('התקן מערכת מצלמות אבטחה')).toBeInTheDocument()
    })

    it('does not render recommendations section when empty', () => {
      const resultWithoutRecommendations = {
        ...mockResult,
        recommendations: {
          immediate_actions: [],
          estimated_complexity: 'low'
        }
      }
      render(<ResultsDisplay result={resultWithoutRecommendations} />)
      
      expect(screen.queryByText('המלצות לפעולה')).not.toBeInTheDocument()
    })

    it('renders recommendations as a list', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      const recommendationsList = screen.getByText('המלצות לפעולה').parentElement?.querySelector('ul')
      expect(recommendationsList).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('handles completely empty result', () => {
      const emptyResult = {}
      render(<ResultsDisplay result={emptyResult} />)
      
      expect(screen.getByText('תוצאות הניתוח')).toBeInTheDocument()
    })

    it('handles null result gracefully', () => {
      render(<ResultsDisplay result={null as any} />)

      // Should render nothing when result is null
      expect(screen.queryByText('תוצאות הניתוח')).not.toBeInTheDocument()
    })

    it('handles undefined result gracefully', () => {
      render(<ResultsDisplay result={undefined as any} />)
      
      // Should render nothing when result is undefined
      expect(screen.queryByText('תוצאות הניתוח')).not.toBeInTheDocument()
    })

    it('handles missing user input', () => {
      const resultWithoutUserInput = {
        ...mockResult,
        user_input: null
      }
      render(<ResultsDisplay result={resultWithoutUserInput} />)
      
      expect(screen.getByText('פרופיל העסק')).toBeInTheDocument()
    })

    it('handles missing attributes array', () => {
      const resultWithoutAttributes = {
        ...mockResult,
        user_input: { ...mockResult.user_input, attributes: null }
      }
      render(<ResultsDisplay result={resultWithoutAttributes} />)
      
      expect(screen.getByText('פרופיל העסק')).toBeInTheDocument()
    })
  })

  describe('RTL Styling', () => {
    it('applies RTL styling to all sections', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      const title = screen.getByText('תוצאות הניתוח')
      expect(title).toHaveStyle({
        textAlign: 'right'
      })
    })

    it('applies RTL styling to business profile section', () => {
      render(<ResultsDisplay result={mockResult} />)
      
      const businessProfile = screen.getByText('פרופיל העסק').parentElement
      expect(businessProfile).toHaveStyle({
        direction: 'rtl',
        textAlign: 'right'
      })
    })
  })
})
