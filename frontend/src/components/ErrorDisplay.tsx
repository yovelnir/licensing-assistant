interface ErrorDisplayProps {
  error: string
}

export const ErrorDisplay = ({ error }: ErrorDisplayProps) => {
  if (!error) return null

  return (
    <div style={{ 
      padding: 16, 
      backgroundColor: '#fee', 
      border: '1px solid #f88', 
      borderRadius: 4,
      marginBottom: 24,
      whiteSpace: 'pre-line',
      direction: 'rtl',
      textAlign: 'right'
    }}>
      <strong style={{ color: '#d00' }}>שגיאה:</strong> {error}
    </div>
  )
}
