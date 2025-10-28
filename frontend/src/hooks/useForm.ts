import { useState } from 'react'
import { useAIAnalysis } from './useApi'

export const useForm = (questions: any[]) => {
  const [answers, setAnswers] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [result, setResult] = useState<any | null>(null)
  const [aiError, setAiError] = useState<string>('')
  const [isAIOnlyMode, setIsAIOnlyMode] = useState(false)
  
  const { analyzeWithAI, generateAIReport, loading: aiApiLoading } = useAIAnalysis()

  const onChange = (name: string, value: any) => {
    setAnswers((prev) => ({ ...prev, [name]: value }))
    // Clear error when user makes changes
    if (error) {
      setError('')
    }
  }

  const validateForm = (): string[] => {
    const errors: string[] = []
    const requiredFields = questions?.filter(q => q.required).map(q => q.name) || []
    
    for (const fieldName of requiredFields) {
      const value = answers[fieldName]
      if (value === null || value === undefined || value === '') {
        const question = questions?.find(q => q.name === fieldName)
        errors.push(`${question?.label} - שדה חובה`)
      }
    }
    
    // Validate numeric ranges per משימה.md requirements
    if (answers.size_m2 !== null && answers.size_m2 !== undefined && answers.size_m2 !== '') {
      const size = Number(answers.size_m2)
      if (isNaN(size) || size <= 0 || size > 10000) {
        errors.push('גודל העסק חייב להיות בין 1 ל-10,000 מ"ר')
      }
    }
    
    if (answers.seats !== null && answers.seats !== undefined && answers.seats !== '') {
      const seats = Number(answers.seats)
      if (isNaN(seats) || seats < 0 || seats > 1000) {
        errors.push('מספר מקומות הישיבה חייב להיות בין 0 ל-1,000')
      }
    }
    
    return errors
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    // Client-side validation per משימה.md requirements
    const validationErrors = validateForm()
    if (validationErrors.length > 0) {
      setError('שגיאות בטופס:\n' + validationErrors.join('\n'))
      return
    }
    
    setLoading(true)
    try {
      const { post } = await import('./useApi')
      const data = await post(`/analyze`, answers)
      setResult(data)
    } catch (err: any) {
      // Handle Hebrew error messages from backend
      if (err.message.includes('HTTP 400')) {
        setError('נתונים לא תקינים - אנא בדוק את השדות החובה')
      } else if (err.message.includes('HTTP 500')) {
        setError('שגיאה בשרת - אנא נסה שוב מאוחר יותר')
      } else {
        setError(`שגיאה: ${err.message}`)
      }
    } finally {
      setLoading(false)
    }
  }

  const onSubmitWithAI = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setAiError('')
    setIsAIOnlyMode(false) // Full analysis mode
    
    // Client-side validation per משימה.md requirements
    const validationErrors = validateForm()
    if (validationErrors.length > 0) {
      setError('שגיאות בטופס:\n' + validationErrors.join('\n'))
      return
    }
    
    try {
      const data = await analyzeWithAI(answers)
      setResult(data)
    } catch (err: any) {
      // Handle Hebrew error messages from backend
      if (err.message.includes('HTTP 400')) {
        setAiError('נתונים לא תקינים - אנא בדוק את השדות החובה')
      } else if (err.message.includes('HTTP 500')) {
        setAiError('שגיאה בשרת - אנא נסה שוב מאוחר יותר')
      } else {
        setAiError(`שגיאה: ${err.message}`)
      }
    }
  }

  const generateAIReportOnly = async (reportType: string = 'comprehensive') => {
    setAiError('')
    setIsAIOnlyMode(true) // AI-only mode
    
    try {
      const data = await generateAIReport(answers, reportType)
      setResult(data)
    } catch (err: any) {
      setAiError(`שגיאה ביצירת דוח AI: ${err.message}`)
    }
  }

  // Calculate form completion for משימה.md requirements
  const requiredFields = questions?.filter(q => q.required).map(q => q.name) || []
  const completedRequired = requiredFields.filter(field => 
    answers[field] !== null && answers[field] !== undefined && answers[field] !== ''
  ).length
  
  // Check if form is valid (all required fields filled AND no validation errors)
  const validationErrors = validateForm()
  const hasValidationErrors = validationErrors.length > 0
  const isFormValid = completedRequired === requiredFields.length && !hasValidationErrors

  return {
    answers,
    loading,
    error,
    result,
    onChange,
    onSubmit,
    onSubmitWithAI,
    generateAIReportOnly,
    isFormValid,
    completedRequired,
    requiredFields,
    validationErrors,
    aiLoading: aiApiLoading,
    aiError,
    isAIOnlyMode
  }
}
