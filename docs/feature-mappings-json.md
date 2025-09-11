# Feature Mappings JSON Configuration

## Overview

The feature mappings system has been migrated from hardcoded Python dictionaries to a flexible JSON configuration file. This allows for easy management of feature labels, descriptions, categories, and display properties without code changes.

## Configuration File

### Location
`backend/app/data/feature-mappings.json`

### Structure
```json
{
  "feature_mappings": {
    "גז": {
      "label": "שימוש בגז",
      "description": "גז למטבח, חימום או שימושים אחרים",
      "category": "בטיחות",
      "icon": "gas",
      "priority": "high"
    }
  },
  "categories": {
    "בטיחות": {
      "label": "בטיחות",
      "description": "דרישות בטיחות ואש",
      "color": "#ff6b6b",
      "icon": "shield"
    }
  },
  "settings": {
    "exclude_mandatory_from_questions": true,
    "default_priority": "medium",
    "show_categories": true,
    "group_by_category": false
  }
}
```

## Feature Mapping Properties

### Core Properties
- **`label`**: User-friendly display name
- **`description`**: Detailed description for tooltips/help text
- **`category`**: Feature category for grouping
- **`icon`**: Icon identifier for UI display
- **`priority`**: Display priority (mandatory, high, medium, low)

### Optional Properties
- **`exclude_from_questions`**: Boolean to exclude from questionnaire
- **`color`**: Custom color for UI display
- **`tooltip`**: Additional tooltip text

### Example Feature Mapping
```json
{
  "גז": {
    "label": "שימוש בגז",
    "description": "גז למטבח, חימום או שימושים אחרים",
    "category": "בטיחות",
    "icon": "gas",
    "priority": "high",
    "exclude_from_questions": false
  }
}
```

## Categories Configuration

### Category Properties
- **`label`**: Display name for the category
- **`description`**: Category description
- **`color`**: Hex color code for UI theming
- **`icon`**: Icon identifier for the category

### Example Category
```json
{
  "בטיחות": {
    "label": "בטיחות",
    "description": "דרישות בטיחות ואש",
    "color": "#ff6b6b",
    "icon": "shield"
  }
}
```

## Settings Configuration

### Available Settings
- **`exclude_mandatory_from_questions`**: Exclude mandatory fields (size, seating) from questionnaire
- **`default_priority`**: Default priority for features without explicit priority
- **`show_categories`**: Whether to display categories in UI
- **`group_by_category`**: Whether to group features by category

### Example Settings
```json
{
  "settings": {
    "exclude_mandatory_from_questions": true,
    "default_priority": "medium",
    "show_categories": true,
    "group_by_category": false
  }
}
```

## Priority System

### Priority Levels
1. **`mandatory`**: Required fields (size, seating)
2. **`high`**: Critical safety features (gas, alcohol)
3. **`medium`**: Important features (cameras, smoking)
4. **`low`**: Optional features

### Sorting
Features are automatically sorted by priority in the questionnaire options.

## API Integration

### Helper Functions
```python
# Load feature mappings
mappings_config = load_feature_mappings_from_json()

# Create question options with enhanced properties
feature_options = create_feature_question_options(features_data)

# Get categories
categories = get_feature_categories()

# Get settings
settings = get_feature_mapping_settings()
```

### Enhanced Question Options
The API now returns enhanced option objects:
```json
{
  "value": "גז",
  "label": "שימוש בגז",
  "description": "גז למטבח, חימום או שימושים אחרים",
  "category": "בטיחות",
  "priority": "high",
  "icon": "gas"
}
```

## Benefits

### 1. **Maintainability**
- ✅ **Non-developer friendly**: Content can be modified without code changes
- ✅ **Centralized configuration**: All feature mappings in one file
- ✅ **Version control**: Changes tracked in JSON files

### 2. **Flexibility**
- ✅ **Dynamic properties**: Add new properties without code changes
- ✅ **Category system**: Organize features by regulatory categories
- ✅ **Priority system**: Control display order and importance

### 3. **Enhanced UI Support**
- ✅ **Icons**: Support for icon-based UI
- ✅ **Colors**: Category-based color theming
- ✅ **Tooltips**: Rich descriptions and help text
- ✅ **Grouping**: Category-based feature organization

## Migration from Hardcoded

### Before (Hardcoded)
```python
feature_mappings = {
    "גז": {
        "label": "שימוש בגז",
        "description": "גז למטבח, חימום או שימושים אחרים"
    }
}
```

### After (JSON Configuration)
```json
{
  "feature_mappings": {
    "גז": {
      "label": "שימוש בגז",
      "description": "גז למטבח, חימום או שימושים אחרים",
      "category": "בטיחות",
      "icon": "gas",
      "priority": "high"
    }
  }
}
```

## Adding New Features

### 1. Add to features.json
```json
{
  "חדש": {
    "categories": {
      "משרד הבריאות": ["חדש", "מילה"]
    },
    "keywords": ["חדש"]
  }
}
```

### 2. Add to feature-mappings.json
```json
{
  "feature_mappings": {
    "חדש": {
      "label": "תכונה חדשה",
      "description": "תיאור התכונה החדשה",
      "category": "אחר",
      "icon": "new",
      "priority": "medium"
    }
  }
}
```

### 3. Restart Application
The new feature will automatically appear in the questionnaire.

## Frontend Integration

### Enhanced Option Structure
```javascript
// Frontend can now access enhanced properties
option.category    // "בטיחות"
option.priority    // "high"
option.icon        // "gas"
option.description // "גז למטבח, חימום או שימושים אחרים"
```

### Category-Based UI
```javascript
// Group options by category
const groupedOptions = options.reduce((groups, option) => {
  const category = option.category;
  if (!groups[category]) groups[category] = [];
  groups[category].push(option);
  return groups;
}, {});
```

### Priority-Based Sorting
```javascript
// Sort by priority
const priorityOrder = { mandatory: 0, high: 1, medium: 2, low: 3 };
options.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
```

## Testing

### Manual Testing
1. Modify `feature-mappings.json`
2. Add new features or change properties
3. Test API endpoint `/questions`
4. Verify enhanced properties in response

### Automated Testing
```python
def test_feature_mappings():
    mappings_config = load_feature_mappings_from_json()
    assert mappings_config is not None
    assert "feature_mappings" in mappings_config
    assert "categories" in mappings_config
    assert "settings" in mappings_config
```

## Best Practices

### 1. **JSON Structure**
- Use consistent naming conventions
- Include all required properties
- Validate JSON syntax before deployment

### 2. **Content Management**
- Keep Hebrew text properly encoded (UTF-8)
- Use descriptive labels and descriptions
- Maintain consistent category naming

### 3. **Priority Management**
- Use appropriate priority levels
- Keep mandatory fields as "mandatory"
- Use "high" for safety-critical features

## Future Enhancements

### Potential Improvements
1. **Admin Interface**: Web UI for managing feature mappings
2. **Database Storage**: Migrate from JSON to database
3. **Internationalization**: Multi-language support
4. **Dynamic Categories**: Runtime category creation
5. **Feature Dependencies**: Define feature relationships

### Additional Properties
1. **`validation_rules`**: Feature-specific validation
2. **`dependencies`**: Required other features
3. **`conflicts`**: Incompatible features
4. **`cost_impact`**: Regulatory cost implications

## Conclusion

The JSON-based feature mappings system provides a flexible, maintainable way to manage feature definitions and UI properties. This approach separates content from code, making the system more accessible to non-developers while providing rich metadata for enhanced user interfaces.

**Key Metrics**:
- **Configuration files**: 1 new JSON file created
- **Hardcoded mappings**: Completely removed
- **Enhanced properties**: 4 new properties per feature
- **Categories**: 5 regulatory categories defined
- **Maintainability**: Significantly improved
