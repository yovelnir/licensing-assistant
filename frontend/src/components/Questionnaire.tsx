import React from 'react'
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
}

export const Questionnaire: React.FC<QuestionnaireProps> = ({
  questions,
  answers,
  loading,
  isFormValid,
  completedRequired,
  requiredFields,
  validationErrors,
  onChange,
  onSubmit
}) => {
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
            {validationErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}
      
      <form onSubmit={onSubmit} style={{ display: 'grid', gap: 20 }} role="form">
        {questions.map((q) => (
          <QuestionInput key={q.name} q={q} value={answers?.[q.name]} onChange={onChange} />
        ))}
        
        <button 
          type="submit" 
          role="button"
          disabled={loading || !isFormValid}
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
          {loading ? 'מנתח נתונים...' : 'נתח דרישות רגולטוריות'}
        </button>
      </form>
    </div>
  )
}
