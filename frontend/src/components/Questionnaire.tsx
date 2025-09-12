import { QuestionInput } from './QuestionInput'

interface QuestionnaireProps {
  questions: any[]
  answers: Record<string, any>
  loading: boolean
  isFormValid: boolean
  completedRequired: number
  requiredFields: string[]
  validationErrors: string[]
  onChange: (name: string, value: any) => void
  onSubmit: (e: React.FormEvent) => void
  onSubmitWithAI?: (e: React.FormEvent) => void
  generateAIReportOnly?: (reportType: string) => void
  aiLoading?: boolean
  aiError?: string
}

export const Questionnaire = ({
  questions,
  answers,
  loading,
  isFormValid,
  completedRequired,
  requiredFields,
  validationErrors,
  onChange,
  onSubmit,
  onSubmitWithAI,
  generateAIReportOnly,
  aiLoading = false,
  aiError = ''
}: QuestionnaireProps) => {
  if (!questions || questions.length === 0) {
    return (
      <div style={{ 
        backgroundColor: '#f9f9f9', 
        padding: 20, 
        borderRadius: 8, 
        marginBottom: 24,
        border: '1px solid #e0e0e0' 
      }}>
        <h2 style={{ margin: '0 0 16px 0', color: '#333' }}>שאלון עסק</h2>
        <p style={{ textAlign: 'center', color: '#666' }}>טוען שאלון...</p>
      </div>
    )
  }

  return (
    <div style={{ 
      backgroundColor: '#f9f9f9', 
      padding: 20, 
      borderRadius: 8, 
      marginBottom: 24,
      border: '1px solid #e0e0e0',
      direction: 'rtl',
      textAlign: 'right'
    }}
    >
      <h2 style={{ 
        margin: '0 0 16px 0', 
        color: '#333',
        textAlign: 'right'
      }}>שאלון עסק</h2>
      
      <div style={{ 
        marginBottom: 16, 
        padding: 12, 
        backgroundColor: '#e8f4fd', 
        borderRadius: 4,
        fontSize: 14,
        textAlign: 'right',
        direction: 'rtl'
      }}>
        <strong>הוראות מילוי:</strong> יש למלא את השדות הנדרשים (מסומנים ב-<span style={{ color: 'red' }}>*</span>) 
        לקבלת ניתוח מדויק של הדרישות הרגולטוריות
        <br />
        <span style={{ color: isFormValid ? 'green' : '#d68910' }}>
          שדות חובה שהושלמו: {completedRequired}/{requiredFields.length}
        </span>
      </div>
      
      {/* Display validation errors */}
      {validationErrors.length > 0 && (
        <div style={{
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          color: '#721c24',
          padding: 12,
          borderRadius: 4,
          marginBottom: 16,
          direction: 'rtl',
          textAlign: 'right'
        }}>
          <strong>שגיאות בטופס:</strong>
          <ul style={{ margin: '8px 0 0 0', paddingRight: 20 }}>
            {validationErrors.map((error: string, index: number) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Display AI errors */}
      {aiError && (
        <div style={{
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          color: '#721c24',
          padding: 12,
          borderRadius: 4,
          marginBottom: 16,
          direction: 'rtl',
          textAlign: 'right'
        }}>
          <strong>שגיאה ב-AI:</strong> {aiError}
        </div>
      )}
      
      <form onSubmit={onSubmit} style={{ display: 'grid', gap: 20 }} role="form">
        {questions.map((q: any) => (
          <QuestionInput key={q.name} q={q} value={answers?.[q.name]} onChange={onChange} />
        ))}
        
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
          <button 
            type="submit" 
            role="button"
            disabled={loading || !isFormValid || aiLoading}
            style={{
              padding: '12px 24px',
              fontSize: 16,
              fontWeight: 'bold',
              backgroundColor: isFormValid ? '#007bff' : '#ccc',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              cursor: isFormValid ? 'pointer' : 'not-allowed',
              transition: 'background-color 0.2s'
            }}
          >
            {loading || aiLoading ? 'מנתח נתונים...' : 'נתח דרישות רגולטוריות'}
          </button>

          {onSubmitWithAI && (
            <button 
              type="button"
              role="button"
              onClick={onSubmitWithAI}
              disabled={aiLoading || !isFormValid || loading}
              style={{
                padding: '12px 24px',
                fontSize: 16,
                fontWeight: 'bold',
                backgroundColor: isFormValid ? '#28a745' : '#ccc',
                color: 'white',
                border: 'none',
                borderRadius: 6,
                cursor: isFormValid ? 'pointer' : 'not-allowed',
                transition: 'background-color 0.2s'
              }}
            >
              {aiLoading ? '🤖 יוצר דוח AI...' : '🤖 ניתוח עם AI'}
            </button>
          )}

          {generateAIReportOnly && (
            <button 
              type="button"
              role="button"
              onClick={() => generateAIReportOnly('comprehensive')}
              disabled={aiLoading || !isFormValid || loading}
              style={{
                padding: '12px 24px',
                fontSize: 16,
                fontWeight: 'bold',
                backgroundColor: isFormValid ? '#6f42c1' : '#ccc',
                color: 'white',
                border: 'none',
                borderRadius: 6,
                cursor: isFormValid ? 'pointer' : 'not-allowed',
                transition: 'background-color 0.2s'
              }}
            >
              {aiLoading ? '📄 יוצר דוח...' : '📄 דוח AI בלבד'}
            </button>
          )}
        </div>
      </form>
    </div>
  )
}
