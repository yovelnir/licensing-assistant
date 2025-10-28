import React from 'react'
import { Header, Questionnaire, ErrorDisplay, ResultsDisplay } from '../components'
import { useHealthCheck, useQuestions, useForm } from '../hooks'

export const App: React.FC = () => {
  const health = useHealthCheck()
  const { questions, loading: questionsLoading, error: questionsError } = useQuestions()
  const {
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
    aiLoading,
    aiError,
    isAIOnlyMode
  } = useForm(questions)

  return (
    <div style={{ 
      fontFamily: 'system-ui, sans-serif', 
      padding: 24, 
      maxWidth: 800,
      margin: '0 auto',
      lineHeight: 1.6,
      direction: 'rtl',
      textAlign: 'right'
    }}>
      <Header health={health} />

      <Questionnaire
        questions={questions}
        answers={answers}
        loading={loading}
        isFormValid={isFormValid}
        completedRequired={completedRequired}
        requiredFields={requiredFields}
        validationErrors={validationErrors}
        onChange={onChange}
        onSubmit={onSubmit}
        onSubmitWithAI={onSubmitWithAI}
        generateAIReportOnly={generateAIReportOnly}
        aiLoading={aiLoading}
        aiError={aiError}
      />

      <ErrorDisplay error={error || questionsError} />

      {<ResultsDisplay result={result ? result : {}} aiLoading={aiLoading} showOnlyAIReport={result ? isAIOnlyMode : true} />}
    </div>
  )
}
