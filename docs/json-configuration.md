# JSON Configuration Documentation

## Overview

The licensing assistant system now uses JSON configuration files for better maintainability and flexibility. This allows non-developers to modify questionnaire content, validation rules, and feature definitions without touching the code.

## Configuration Files

### 1. Questions Configuration (`backend/app/data/questions.json`)

**Purpose**: Defines the questionnaire structure, validation rules, and metadata.

**Structure**:
```json
{
  "questionnaire": {
    "version": "1.1",
    "description": "שאלון רישוי עסקים מסעדות לפי משימה טכנית",
    "instructions": "יש למלא לפחות את השדות הנדרשים (גודל ותפוסה) כדי לקבל ניתוח מדויק",
    "required_fields": ["size_m2", "seats"]
  },
  "questions": [
    {
      "name": "size_m2",
      "label": "גודל העסק (מ\"ר)",
      "type": "number",
      "required": true,
      "min": 1,
      "max": 10000,
      "placeholder": "לדוגמה: 150",
      "description": "שטח העסק במטרים מרובעים - נדרש לצורך סינון דרישות"
    }
  ],
  "validation": {
    "size_m2": {
      "min": 1,
      "max": 10000,
      "error_message": "גודל העסק חייב להיות בין 1 ל-10,000 מ\"ר"
    }
  }
}
```

**Fields**:
- `questionnaire`: Global questionnaire settings
- `questions`: Array of question definitions
- `validation`: Field-specific validation rules

### 2. Features Configuration (`backend/app/data/raw/features.json`)

**Purpose**: Defines available business features and their keywords for dynamic matching.

**Structure**:
```json
{
  "גז": {
    "categories": {
      "משרד הבריאות": ["גז", "מערכת גז", "בלוני גז"],
      "בטיחות אש": ["גז", "דליפת גז", "וסתי גז"]
    },
    "keywords": ["גז"]
  }
}
```

## Question Types

### Number Questions
```json
{
  "name": "size_m2",
  "label": "גודל העסק (מ\"ר)",
  "type": "number",
  "required": true,
  "min": 1,
  "max": 10000,
  "placeholder": "לדוגמה: 150",
  "description": "שטח העסק במטרים מרובעים"
}
```

**Properties**:
- `name`: Field identifier
- `label`: Display label
- `type`: Input type ("number")
- `required`: Whether field is mandatory
- `min`/`max`: Numeric constraints
- `placeholder`: Input placeholder text
- `description`: Help text

### Multiselect Questions
```json
{
  "name": "attributes",
  "label": "מאפייני עסק נוספים",
  "type": "multiselect",
  "required": false,
  "description": "בחר את כל המאפיינים הרלוונטיים"
}
```

**Properties**:
- `name`: Field identifier
- `label`: Display label
- `type`: Input type ("multiselect")
- `required`: Whether field is mandatory
- `description`: Help text
- `options`: Dynamically populated from features.json

## Validation Rules

### Field Validation
```json
{
  "validation": {
    "size_m2": {
      "min": 1,
      "max": 10000,
      "error_message": "גודל העסק חייב להיות בין 1 ל-10,000 מ\"ר"
    },
    "seats": {
      "min": 0,
      "max": 1000,
      "error_message": "מספר מקומות הישיבה חייב להיות בין 0 ל-1,000"
    }
  }
}
```

**Properties**:
- `min`/`max`: Numeric range constraints
- `error_message`: Custom error message in Hebrew

## Dynamic Features

### Feature Definition
```json
{
  "גז": {
    "categories": {
      "משרד הבריאות": ["גז", "מערכת גז", "בלוני גז"],
      "בטיחות אש": ["גז", "דליפת גז", "וסתי גז"]
    },
    "keywords": ["גז"]
  }
}
```

**Properties**:
- `categories`: Regulatory categories and their keywords
- `keywords`: General keywords for matching

### Feature Mappings
The system automatically maps features to user-friendly labels:

```python
feature_mappings = {
    "גז": {
        "label": "שימוש בגז",
        "description": "גז למטבח, חימום או שימושים אחרים"
    },
    "מצלמות": {
        "label": "מצלמות אבטחה",
        "description": "מערכת מצלמות אבטחה (CCTV)"
    }
}
```

## API Integration

### Questions Endpoint
The `/questions` endpoint automatically loads configuration from JSON files:

```python
@api_blueprint.get("/questions")
def get_questions():
    features_data = load_features_from_json()
    feature_options = create_feature_question_options(features_data)
    questions, metadata = create_questionnaire_from_json(feature_options)
    
    return jsonify({
        "questions": questions,
        "metadata": metadata
    })
```

### Validation
Input validation uses the JSON configuration:

```python
def validate_user_input(payload):
    questions_config = load_questions_from_json()
    validation_rules = questions_config.get("validation", {})
    # Apply validation rules from JSON
```

## Fallback Mechanism

If JSON files cannot be loaded, the system falls back to hardcoded values:

```python
def create_questionnaire_from_json(feature_options):
    questions_config = load_questions_from_json()
    
    if not questions_config:
        # Fallback to hardcoded questions
        return _create_fallback_questions(feature_options)
    
    # Use JSON configuration
    return questions, metadata
```

## Benefits

### 1. **Maintainability**
- ✅ **Non-developer friendly**: Content can be modified without code changes
- ✅ **Version control**: Changes tracked in JSON files
- ✅ **Easy updates**: Modify questions, validation rules, and features

### 2. **Flexibility**
- ✅ **Dynamic content**: Questions and features loaded at runtime
- ✅ **Configurable validation**: Error messages and rules in JSON
- ✅ **Multilingual support**: Easy to add new languages

### 3. **Scalability**
- ✅ **Easy to extend**: Add new questions or features
- ✅ **Modular design**: Separate concerns in different files
- ✅ **Future-proof**: Easy to migrate to database storage

## File Structure

```
backend/app/data/
├── questions.json          # Questionnaire configuration
└── raw/
    └── features.json       # Feature definitions
```

## Best Practices

### 1. **JSON Structure**
- Use consistent naming conventions
- Include comprehensive error messages
- Validate JSON syntax before deployment

### 2. **Content Management**
- Keep Hebrew text properly encoded (UTF-8)
- Use descriptive field names
- Include helpful descriptions and placeholders

### 3. **Validation Rules**
- Set appropriate min/max values
- Provide clear error messages
- Test validation with edge cases

## Testing

### Manual Testing
1. Modify `questions.json` to change question text
2. Update validation rules in the same file
3. Add new features to `features.json`
4. Test API endpoints to verify changes

### Automated Testing
```python
def test_json_questions():
    questions_config = load_questions_from_json()
    assert questions_config is not None
    assert "questionnaire" in questions_config
    assert "questions" in questions_config
    assert "validation" in questions_config
```

## Migration Guide

### From Hardcoded to JSON
1. **Extract questions**: Move hardcoded questions to `questions.json`
2. **Extract validation**: Move validation rules to JSON
3. **Update code**: Modify helper functions to load from JSON
4. **Test thoroughly**: Ensure all functionality works

### Future Enhancements
1. **Database storage**: Migrate from JSON to database
2. **Admin interface**: Web UI for managing questions
3. **Versioning**: Support multiple questionnaire versions
4. **A/B testing**: Support different question sets

## Conclusion

The JSON configuration system provides a flexible, maintainable way to manage questionnaire content and validation rules. This approach separates content from code, making the system more accessible to non-developers while maintaining the robustness of the underlying matching algorithms.
