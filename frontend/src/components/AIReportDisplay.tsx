import { useState } from 'react'

interface AIReportProps {
  aiReport: {
    content: string
    provider: string
    model_used?: string
    tokens_used?: number
    success: boolean
    error_message?: string
    generation_timestamp?: string
  }
  loading?: boolean
}

export const AIReportDisplay = ({ aiReport, loading = false }: AIReportProps) => {
  const [isExpanded, setIsExpanded] = useState(false)

  if (loading) {
    return (
      <div style={{
        padding: '20px',
        border: '2px solid #e0e0e0',
        borderRadius: '8px',
        margin: '20px 0',
        backgroundColor: '#f9f9f9',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '18px', marginBottom: '10px' }}>🤖</div>
        <div>יוצר דוח חכם באמצעות AI...</div>
        <div style={{ fontSize: '14px', color: '#666', marginTop: '10px' }}>
          זה יכול לקחת כמה שניות
        </div>
      </div>
    )
  }

  if (!aiReport.success) {
    return (
      <div style={{
        padding: '20px',
        border: '2px solid #ff6b6b',
        borderRadius: '8px',
        margin: '20px 0',
        backgroundColor: '#ffe0e0',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '18px', marginBottom: '10px' }}>⚠️</div>
        <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>
          לא ניתן ליצור דוח AI
        </div>
        <div style={{ fontSize: '14px', color: '#666' }}>
          {aiReport.error_message || 'שגיאה לא ידועה - אנא בדוק את מפתח ה-API'}
        </div>
        {aiReport.provider && (
          <div style={{ fontSize: '12px', color: '#999', marginTop: '8px' }}>
            ספק AI: {aiReport.provider}
          </div>
        )}
      </div>
    )
  }

  const formatContent = (content: string) => {
    // Enhanced markdown parser with better formatting
    const lines = content.split('\n')
    const elements: JSX.Element[] = []
    let currentList: string[] = []
    let currentOrderedList: string[] = []
    let currentTable: string[][] = []
    let inTable = false
    let listIndex = 1
    
    const flushList = () => {
      if (currentList.length > 0) {
        elements.push(
          <ul key={`list-${elements.length}`} style={{
            margin: '10px 0',
            paddingRight: '20px',
            listStyleType: 'disc'
          }}>
            {currentList.map((item, idx) => (
              <li key={idx} style={{ marginBottom: '5px', lineHeight: '1.5' }}>
                {formatInlineMarkdown(item)}
              </li>
            ))}
          </ul>
        )
        currentList = []
      }
    }
    
    const flushOrderedList = () => {
      if (currentOrderedList.length > 0) {
        elements.push(
          <ol key={`olist-${elements.length}`} style={{
            margin: '10px 0',
            paddingRight: '20px',
            listStyleType: 'decimal'
          }}>
            {currentOrderedList.map((item, idx) => (
              <li key={idx} style={{ marginBottom: '5px', lineHeight: '1.5' }}>
                {formatInlineMarkdown(item)}
              </li>
            ))}
          </ol>
        )
        currentOrderedList = []
        listIndex = 1
      }
    }
    
    const flushTable = () => {
      if (currentTable.length > 0) {
        const [header, ...rows] = currentTable
        elements.push(
          <div key={`table-${elements.length}`} style={{
            margin: '15px 0',
            overflowX: 'auto',
            border: '1px solid #ddd',
            borderRadius: '6px',
            backgroundColor: 'white'
          }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '14px',
              direction: 'rtl'
            }}>
              {header && (
                <thead>
                  <tr style={{ backgroundColor: '#f8f9fa' }}>
                    {header.map((cell, idx) => (
                      <th key={idx} style={{
                        padding: '12px 8px',
                        textAlign: 'right',
                        borderBottom: '2px solid #dee2e6',
                        fontWeight: 'bold',
                        color: '#495057'
                      }}>
                        {formatInlineMarkdown(cell.trim())}
                      </th>
                    ))}
                  </tr>
                </thead>
              )}
              <tbody>
                {rows.map((row, rowIdx) => (
                  <tr key={rowIdx} style={{
                    borderBottom: '1px solid #dee2e6'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f8f9fa'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent'
                  }}>
                    {row.map((cell, cellIdx) => (
                      <td key={cellIdx} style={{
                        padding: '10px 8px',
                        textAlign: 'right',
                        verticalAlign: 'top'
                      }}>
                        {formatInlineMarkdown(cell.trim())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
        currentTable = []
        inTable = false
      }
    }
    
    const formatInlineMarkdown = (text: string) => {
      // Handle bold text **text**
      let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      
      // Handle italic text *text*
      formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>')
      
      // Handle inline code `code`
      formatted = formatted.replace(/`(.*?)`/g, '<code style="background: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-family: monospace;">$1</code>')
      
      return <span dangerouslySetInnerHTML={{ __html: formatted }} />
    }
    
    lines.forEach((line, index) => {
      const trimmedLine = line.trim()
      
      // Handle table rows (detect pipe-separated values)
      if (trimmedLine.includes('|') && trimmedLine.split('|').length > 2) {
        flushList()
        flushOrderedList()
        
        // Skip separator rows (e.g., |---|---|)
        if (!trimmedLine.match(/^\|[\s\-\|]+\|$/)) {
          const cells = trimmedLine.split('|').map(cell => cell.trim()).filter(cell => cell)
          currentTable.push(cells)
          inTable = true
        }
        return
      }
      
      // Handle headers
      if (trimmedLine.match(/^#{1,6}\s/)) {
        flushList()
        flushOrderedList()
        flushTable()
        
        const headerLevel = trimmedLine.match(/^#+/)?.[0].length || 0
        const headerText = trimmedLine.replace(/^#+\s*/, '')
        const HeaderTag = `h${Math.min(headerLevel + 2, 6)}` as keyof JSX.IntrinsicElements
        
        elements.push(
          <HeaderTag key={index} style={{
            color: '#2c3e50',
            margin: '20px 0 10px 0',
            paddingBottom: '8px',
            borderBottom: headerLevel <= 2 ? '2px solid #3498db' : '1px solid #bdc3c7',
            fontSize: headerLevel <= 2 ? '24px' : headerLevel === 3 ? '20px' : '18px',
            fontWeight: 'bold'
          }}>
            {headerText}
          </HeaderTag>
        )
      }
      // Handle unordered lists
      else if (trimmedLine.match(/^[-*+]\s/)) {
        flushOrderedList()
        flushTable()
        const listItem = trimmedLine.replace(/^[-*+]\s/, '')
        currentList.push(listItem)
      }
      // Handle ordered lists
      else if (trimmedLine.match(/^\d+\.\s/)) {
        flushList()
        flushTable()
        const listItem = trimmedLine.replace(/^\d+\.\s/, '')
        currentOrderedList.push(listItem)
      }
      // Handle horizontal rules
      else if (trimmedLine.match(/^[-*_]{3,}$/)) {
        flushList()
        flushOrderedList()
        flushTable()
        elements.push(
          <hr key={index} style={{
            border: 'none',
            borderTop: '2px solid #bdc3c7',
            margin: '20px 0'
          }} />
        )
      }
      // Handle code blocks
      else if (trimmedLine.startsWith('```')) {
        flushList()
        flushOrderedList()
        // Skip code block start/end markers for now
        return
      }
      // Handle regular paragraphs
      else if (trimmedLine) {
        flushList()
        flushOrderedList()
        flushTable()
        elements.push(
          <p key={index} style={{
            margin: '10px 0',
            lineHeight: '1.6',
            fontSize: '16px',
            textAlign: 'right'
          }}>
            {formatInlineMarkdown(trimmedLine)}
          </p>
        )
      }
      // Handle empty lines
      else {
        flushList()
        flushOrderedList()
        flushTable()
        elements.push(<br key={index} />)
      }
    })
    
    // Flush any remaining lists and tables
    flushList()
    flushOrderedList()
    flushTable()
    
    return elements
  }

  return (
    <div style={{
      padding: '0',
      border: '2px solid #27ae60',
      borderRadius: '12px',
      margin: '20px 0',
      backgroundColor: '#f0fff4',
      direction: 'rtl',
      textAlign: 'right',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      overflow: 'hidden'
    }}>
      {/* Header with AI info */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '0',
        padding: '20px',
        backgroundColor: '#27ae60',
        color: 'white'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ fontSize: '28px' }}>🤖</div>
          <div>
            <div style={{ fontWeight: 'bold', fontSize: '22px', color: 'white' }}>
              דוח חכם - AI
            </div>
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.9)' }}>
              נוצר באמצעות {aiReport.provider} {aiReport.model_used && `(${aiReport.model_used})`}
            </div>
          </div>
        </div>
        
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          style={{
            padding: '10px 20px',
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            color: 'white',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 'bold',
            transition: 'all 0.2s ease'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.3)'
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.2)'
          }}
        >
          {isExpanded ? 'הסתר' : 'הצג דוח מלא'}
        </button>
      </div>

      {/* AI Report Content */}
      {isExpanded ? (
        <div style={{
          maxHeight: '600px',
          overflowY: 'auto',
          padding: '20px',
          backgroundColor: 'white',
          borderRadius: '6px',
          border: '1px solid #ddd',
          boxShadow: 'inset 0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{
            lineHeight: '1.7',
            fontSize: '16px',
            color: '#2c3e50'
          }}>
            {formatContent(aiReport.content)}
          </div>
        </div>
      ) : (
        <div style={{
          maxHeight: '200px',
          overflow: 'hidden',
          position: 'relative',
          padding: '15px',
          backgroundColor: 'white',
          borderRadius: '6px',
          border: '1px solid #ddd'
        }}>
          <div style={{
            lineHeight: '1.6',
            fontSize: '16px',
            color: '#2c3e50'
          }}>
            {formatContent(aiReport.content.substring(0, 500))}
            {aiReport.content.length > 500 && (
              <div style={{
                display: 'inline-block',
                backgroundColor: '#f8f9fa',
                padding: '2px 6px',
                borderRadius: '3px',
                fontSize: '14px',
                color: '#6c757d',
                marginTop: '10px'
              }}>
                ...
              </div>
            )}
          </div>
          {aiReport.content.length > 500 && (
            <div style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              height: '50px',
              background: 'linear-gradient(transparent, #f0fff4)',
              display: 'flex',
              alignItems: 'end',
              justifyContent: 'center'
            }}>
              <div style={{
                backgroundColor: '#3498db',
                color: 'white',
                padding: '5px 15px',
                borderRadius: '15px',
                fontSize: '12px'
              }}>
                לחץ על "הצג דוח מלא" לראות את כל התוכן
              </div>
            </div>
          )}
        </div>
      )}

      {/* Footer with technical info */}
      <div style={{
        marginTop: '15px',
        padding: '15px 20px',
        borderTop: '1px solid #ddd',
        fontSize: '12px',
        color: '#666',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: '#f8f9fa',
        borderRadius: '0 0 8px 8px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>🔢</span>
          <span>{aiReport.tokens_used && `טוקנים: ${aiReport.tokens_used}`}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>📅</span>
          <span>נוצר ב-{new Date(aiReport.generation_timestamp || Date.now()).toLocaleString('he-IL')}</span>
        </div>
      </div>
    </div>
  )
}
