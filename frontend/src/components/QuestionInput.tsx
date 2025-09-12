interface QuestionInputProps {
  q: any
  value: any
  onChange: (name: string, value: any) => void
}

export const QuestionInput = ({ q, value, onChange }: QuestionInputProps) => {
  const common = { id: q.name, name: q.name }
  const isRequired = q.required || false
  
  // Number input for size and seats per משימה.md requirements
  if (q.type === 'number') {
    return (
      <div style={{ 
        display: 'grid', 
        gap: 6,
        direction: 'rtl',
        textAlign: 'right'
      }}>
        <label htmlFor={q.name} style={{ 
          fontWeight: isRequired ? 'bold' : 'normal',
          textAlign: 'right'
        }}>
          {q.label} {isRequired && <span style={{ color: 'red' }}>*</span>}
        </label>
        <input 
          type="number" 
          {...common} 
          min={q.min} 
          max={q.max} 
          placeholder={q.placeholder}
          value={value ?? ''} 
          onChange={(e) => onChange(q.name, e.target.value === '' ? null : Number(e.target.value))}
          required={isRequired}
          style={{ 
            padding: 8, 
            fontSize: 14, 
            border: '1px solid #ccc', 
            borderRadius: 4,
            direction: 'ltr',
            textAlign: 'left'
          }}
        />
        {q.description && (
          <small style={{ 
            color: '#666', 
            fontSize: 12,
            textAlign: 'right'
          }}>{q.description}</small>
        )}
      </div>
    )
  }
  
  // Boolean input for special characteristics per משימה.md requirements
  if (q.type === 'boolean') {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 6,
        direction: 'rtl',
        textAlign: 'right'
      }}>
        <label style={{ 
          display: 'flex', 
          gap: 8, 
          alignItems: 'center', 
          cursor: 'pointer',
          flexDirection: 'row-reverse'
        }}>
          <input 
            type="checkbox" 
            {...common} 
            checked={!!value} 
            onChange={(e) => onChange(q.name, e.target.checked)}
            style={{ transform: 'scale(1.2)' }}
          />
          <span style={{ 
            fontWeight: isRequired ? 'bold' : 'normal',
            textAlign: 'right'
          }}>
            {q.label} {isRequired && <span style={{ color: 'red' }}>*</span>}
          </span>
        </label>
        {q.description && (
          <small style={{ 
            color: '#666', 
            fontSize: 12, 
            marginRight: 28,
            textAlign: 'right'
          }}>{q.description}</small>
        )}
      </div>
    )
  }
  
  // Multiselect for additional attributes per משימה.md requirements
  if (q.type === 'multiselect') {
    const currentValue = Array.isArray(value) ? value : []
    
    return (
      <div style={{ 
        display: 'grid', 
        gap: 6,
        direction: 'rtl',
        textAlign: 'right'
      }}>
        <label style={{ 
          fontWeight: isRequired ? 'bold' : 'normal',
          textAlign: 'right'
        }}>
          {q.label} {isRequired && <span style={{ color: 'red' }}>*</span>}
        </label>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: 8,
          padding: 12,
          border: '1px solid #ccc',
          borderRadius: 4,
          backgroundColor: '#fafafa',
          direction: 'rtl'
        }}>
          {q.options?.map((option: any) => {
            const isSelected = currentValue.includes(option.value)
            return (
              <label 
                key={option.value} 
                style={{ 
                  display: 'flex', 
                  gap: 8, 
                  alignItems: 'center', 
                  cursor: 'pointer',
                  fontSize: 14,
                  flexDirection: 'row-reverse',
                  textAlign: 'right'
                }}
              >
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={(e) => {
                    const newValue = e.target.checked
                      ? [...currentValue, option.value]
                      : currentValue.filter((v: string) => v !== option.value)
                    onChange(q.name, newValue)
                  }}
                />
                {option.label}
              </label>
            )
          })}
        </div>
        {q.description && (
          <small style={{ 
            color: '#666', 
            fontSize: 12,
            textAlign: 'right'
          }}>{q.description}</small>
        )}
      </div>
    )
  }
  
  return null
}
