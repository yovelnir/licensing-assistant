import React from 'react'

interface ResultsDisplayProps {
  result: any
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result }) => {
  // Early return if no result
  if (!result) {
    return null
  }

  const businessAnalysis = result.business_analysis || {}
  const regulatoryAnalysis = result.regulatory_analysis || {}
  const recommendations = result.recommendations || {}

  return (
    <div style={{ 
      marginTop: 24,
      direction: 'rtl',
      textAlign: 'right'
    }}>
      <h2 style={{ 
        color: '#333', 
        marginBottom: 20,
        textAlign: 'right'
      }}>תוצאות הניתוח</h2>
      
      {/* Business Profile Summary */}
      <div style={{ 
        backgroundColor: '#f0f8ff', 
        padding: 16, 
        borderRadius: 6, 
        marginBottom: 20,
        border: '1px solid #bee5eb',
        direction: 'rtl',
        textAlign: 'right'
      }}>
        <h3 style={{ 
          margin: '0 0 12px 0', 
          color: '#0c5460',
          textAlign: 'right'
        }}>פרופיל העסק</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div>
            <strong>גודל:</strong> {result.user_input?.size_m2} מ"ר 
            ({businessAnalysis.classification?.size_category === 'large' ? 'עסק גדול' : 'עסק קטן'})
          </div>
          <div>
            <strong>תפוסה:</strong> {result.user_input?.seats} מקומות 
            ({businessAnalysis.classification?.occupancy_category === 'high' ? 'תפוסה גבוהה' : 'תפוסה נמוכה'})
          </div>
        </div>
        {result.user_input?.attributes?.length > 0 && (
          <div style={{ marginTop: 8 }}>
            <strong>מאפיינים נוספים:</strong> {result.user_input.attributes.join(', ')}
          </div>
        )}
      </div>

      {/* Regulatory Summary */}
      <div style={{ 
        backgroundColor: '#fff3cd', 
        padding: 16, 
        borderRadius: 6, 
        marginBottom: 20,
        border: '1px solid #ffeaa7'
      }}>
        <h3 style={{ 
          margin: '0 0 12px 0', 
          color: '#856404',
          textAlign: 'right'
        }}>סיכום רגולטורי</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
          <div>
            <strong>סה"כ דרישות:</strong> {regulatoryAnalysis.total_matches || 0}
          </div>
          <div>
            <strong>עדיפות גבוהה:</strong> {regulatoryAnalysis.priority_breakdown?.high || 0}
          </div>
          <div>
            <strong>עדיפות בינונית:</strong> {regulatoryAnalysis.priority_breakdown?.medium || 0}
          </div>
          <div>
            <strong>מורכבות:</strong> {recommendations.estimated_complexity === 'high' ? 'גבוהה' : 'בינונית'}
          </div>
        </div>
      </div>

      {/* Categories */}
      {Object.keys(regulatoryAnalysis.by_category || {}).length > 0 && (
        <div style={{ 
          backgroundColor: 'white', 
          padding: 16, 
          borderRadius: 6, 
          marginBottom: 20,
          border: '1px solid #ddd'
        }}>
          <h3 style={{ margin: '0 0 16px 0', color: '#333' }}>דרישות לפי קטגוריה</h3>
          {Object.entries(regulatoryAnalysis.by_category || {}).map(([category, requirements]: [string, any]) => (
            <details key={category} style={{ marginBottom: 12 }}>
              <summary style={{ 
                cursor: 'pointer', 
                fontWeight: 'bold', 
                padding: '8px 0',
                color: '#0066cc'
              }}>
                {category} ({Array.isArray(requirements) ? requirements.length : 0} דרישות)
              </summary>
              <div style={{ marginTop: 8, paddingRight: 20 }}>
                {Array.isArray(requirements) && requirements.slice(0, 3).map((req: any, idx: number) => (
                  <div key={idx} style={{ 
                    marginBottom: 8, 
                    padding: 8, 
                    backgroundColor: '#f8f9fa',
                    borderRadius: 4,
                    fontSize: 14
                  }}>
                    <div style={{ marginBottom: 4 }}>
                      <strong>סעיף {req.paragraph_number}</strong>
                      <span style={{ 
                        marginRight: 8,
                        padding: '2px 6px',
                        borderRadius: 3,
                        fontSize: 11,
                        backgroundColor: req.priority === 'high' ? '#dc3545' : '#ffc107',
                        color: req.priority === 'high' ? 'white' : 'black'
                      }}>
                        {req.priority === 'high' ? 'עדיפות גבוהה' : 'עדיפות בינונית'}
                      </span>
                    </div>
                    <div style={{ color: '#666' }}>
                      {req.text?.substring(0, 150)}...
                    </div>
                  </div>
                ))}
                {Array.isArray(requirements) && requirements.length > 3 && (
                  <p style={{ color: '#666', fontSize: 12, fontStyle: 'italic' }}>
                    ועוד {requirements.length - 3} דרישות נוספות...
                  </p>
                )}
              </div>
            </details>
          ))}
        </div>
      )}

      {/* Recommendations */}
      {recommendations.immediate_actions?.length > 0 && (
        <div style={{ 
          backgroundColor: '#d1ecf1', 
          padding: 16, 
          borderRadius: 6,
          border: '1px solid #bee5eb'
        }}>
          <h3 style={{ margin: '0 0 12px 0', color: '#0c5460' }}>המלצות לפעולה</h3>
          <ul style={{ margin: 0, paddingRight: 20 }}>
            {recommendations.immediate_actions.map((action: string, idx: number) => (
              <li key={idx} style={{ marginBottom: 4 }}>{action}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
