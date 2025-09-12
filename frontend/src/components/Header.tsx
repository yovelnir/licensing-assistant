interface HeaderProps {
  health: string
}

export const Header = ({ health }: HeaderProps) => {
  return (
    <div style={{ 
      textAlign: 'center', 
      marginBottom: 32,
      direction: 'rtl'
    }}>
      <h1 style={{ 
        color: '#333', 
        marginBottom: 8,
        textAlign: 'center'
      }}>מערכת הערכת רישוי עסקים</h1>
      <p style={{ 
        color: '#666', 
        fontSize: 16,
        textAlign: 'center'
      }}>מסייעת לבעלי עסקים להבין דרישות רגולטוריות</p>
      <p style={{ 
        fontSize: 12, 
        color: health === 'ok' ? 'green' : 'red',
        textAlign: 'center'
      }}>
        סטטוס מערכת: {health === 'ok' ? 'פעילה' : 'לא זמינה'}
      </p>
    </div>
  )
}
