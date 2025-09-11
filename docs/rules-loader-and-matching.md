# Rules Loader and Matching Algorithm Documentation

## Overview

The licensing assistant system uses a sophisticated rules loader and matching algorithm to process regulatory requirements and match them to business characteristics. This document provides comprehensive documentation of the system architecture, design patterns, and implementation details.

## System Architecture

### Design Patterns Used

1. **Singleton Pattern** - Used in `rules_loader.py` with `@lru_cache` for efficient data loading
2. **Repository Pattern** - Used for consistent data access across the system
3. **Specification Pattern** - Used in `matching.py` for complex business rule evaluation

### Data Flow

```
PDF/DOCX Documents → Parser → Processed Data → Rules Loader → Matching Algorithm → API Response
```

## Rules Loader (`rules_loader.py`)

### Purpose

The rules loader provides a centralized data access layer for regulatory requirements. It implements the Repository pattern to abstract data loading and provide consistent interfaces for accessing processed regulatory data.

### Key Components

#### 1. Data Loading Functions

```python
@lru_cache(maxsize=1)
def load_parser_data() -> Tuple[Dict[str, Any], Dict[str, Any]]
```

**Purpose**: Loads processed parser outputs with caching for performance
**Returns**: Tuple of (paragraphs, mappings)
- `paragraphs`: Hierarchical document structure by regulatory category
- `mappings`: Feature-to-paragraph mappings for content classification

**Caching Strategy**: Uses `@lru_cache` with `maxsize=1` to ensure data is loaded only once per application lifecycle

#### 2. Data Access Functions

```python
def get_paragraphs() -> Dict[str, Any]
def get_mappings() -> Dict[str, Any]
def get_paragraph_text(paragraphs: Dict[str, Any], category: str, number: str) -> str
```

**Purpose**: Provide clean interfaces for accessing different data types
**Benefits**: 
- Separation of concerns
- Easy testing and mocking
- Consistent data access patterns

### Data Structure

#### Paragraphs Structure
```json
{
  "הרשות הארצית לכבאות והצלה": {
    "5": {
      "text": "Main section text...",
      "5.1": {
        "text": "Subsection text..."
      }
    }
  }
}
```

#### Mappings Structure
```json
{
  "גז": {
    "categories": {
      "משרד הבריאות": ["5.1", "5.2"],
      "בטיחות אש": ["6.1", "6.2"]
    },
    "paragraphs": ["5.1", "5.2", "6.1", "6.2"]
  }
}
```

## Matching Algorithm (`matching.py`)

### Purpose

The matching algorithm implements intelligent regulatory requirement matching based on business characteristics. It uses multiple strategies including numeric range matching, feature-based filtering, and relevance scoring.

### Key Components

#### 1. Input Normalization

```python
def _normalize_user_input(answers: Dict[str, Any]) -> Dict[str, Any]
```

**Purpose**: Standardize user input for consistent processing
**Features**:
- Handles multiple input formats (size_m2, seats, attributes)
- Extracts boolean flags from various sources
- Ensures JSON serialization compatibility

**Input Support**:
- `size_m2`: Business floor area in square meters
- `seats/seating`: Number of seats/occupancy
- `attributes`: List of business characteristics
- `uses_gas`, `serves_meat`: Boolean flags (legacy support)

#### 2. Numeric Range Extraction

```python
def _extract_numeric_ranges(text: str) -> dict
```

**Purpose**: Extract numeric constraints from Hebrew regulatory text
**Features**:
- Supports Hebrew text patterns for size (מ"ר) and occupancy (איש)
- Handles ranges, minimums, maximums, and exact values
- Uses sophisticated regex patterns for Hebrew text

**Pattern Examples**:
- Ranges: "בין 100 ל-200 מ"ר", "50-80 איש"
- Minimums: "מעל 150 מ"ר", "לפחות 30 איש"
- Maximums: "עד 300 מ"ר", "לא יותר מ-100 איש"
- Exact: "120 מ"ר", "תפוסה של 50 מקומות"

**Return Structure**:
```json
{
  "size_m2": {
    "min": 100,
    "max": 200,
    "exact": [120, 150]
  },
  "occupancy": {
    "min": 30,
    "max": 80,
    "exact": [50]
  }
}
```

#### 3. Numeric Requirement Matching

```python
def _matches_numeric_requirements(user_profile: Dict[str, Any], paragraph_ranges: dict) -> bool
```

**Purpose**: Check if user's business characteristics match numeric requirements
**Logic**:
- Validates size constraints (min/max/exact)
- Validates occupancy constraints (min/max/exact)
- Handles missing data gracefully
- Returns False if requirements exist but user data is insufficient

#### 4. Dynamic Feature Loading

```python
def _load_features_from_json()
```

**Purpose**: Load features dynamically from `features.json`
**Benefits**:
- No hardcoded features in algorithm
- Easy to add new features without code changes
- Supports both string and regex keyword patterns

**Features Structure**:
```json
{
  "גז": {
    "categories": {
      "משרד הבריאות": ["גז", "מערכת גז"],
      "בטיחות אש": ["גז", "דליפת גז"]
    },
    "keywords": ["גז"]
  },
  "מ\"ר": {
    "search_all_categories": true,
    "keywords": [
      {"regex": true, "pattern": "[0-9]+\\s*מ\"ר"},
      {"regex": true, "pattern": "\\d+[\\d.,]*\\s*(?:מ\\\"ר|מ[\\\"\\u05f4'׳]?\\s*ר)"}
    ]
  }
}
```

#### 5. Feature Profile Matching

```python
def _matches_user_profile(user_profile: Dict[str, Any], feature: str) -> bool
```

**Purpose**: Determine if a feature applies to user's business profile
**Logic**:
- Size-related features (מ"ר) - always apply
- Occupancy features (תפוסה) - always apply
- Dynamic features from features.json - only if user selected them
- Safety features - always apply

**Dynamic Feature Handling**:
- Loads features from `features.json` at runtime
- Checks if feature is in user's `attributes` list
- Skips size and occupancy (always applied)
- Falls back to safety features for general requirements

#### 6. Relevance Assessment

```python
def _assess_requirement_relevance(paragraph_text: str, user_profile: Dict[str, Any], paragraph_ranges: dict = None) -> float
```

**Purpose**: Score how relevant a requirement is to user's business
**Scoring Factors**:

1. **Range-based Scoring (0.4 max)**:
   - Size matching: +0.4 for min/max matches, +0.3 for exact proximity
   - Occupancy matching: +0.4 for min/max matches, +0.3 for exact proximity

2. **Dynamic Feature Scoring (0.2 per feature)**:
   - String keyword matches: +0.2
   - Regex pattern matches: +0.2

3. **Safety Priority (0.3)**:
   - High-priority terms: "חירום", "בטיחות", "כיבוי", "emergency", "safety"

4. **Penalties**:
   - Non-matching numeric requirements: ×0.2 penalty

**Final Score**: Capped at 1.0, starts at 0.3 base

#### 7. Main Matching Function

```python
def match_requirements(user_answers: Dict[str, Any], min_relevance: float = 0.3) -> Dict[str, Any]
```

**Purpose**: Main entry point for regulatory requirement matching
**Process**:

1. **Normalize Input**: Convert user answers to standard format
2. **Get Applicable Features**: Determine which features apply to user's business
3. **Collect Paragraphs**: Find all paragraphs mapped to applicable features
4. **Extract Ranges**: Extract numeric constraints from each paragraph
5. **Filter by Requirements**: Skip paragraphs that don't match user's size/occupancy
6. **Score Relevance**: Calculate relevance score for each paragraph
7. **Filter by Relevance**: Keep only paragraphs above minimum threshold
8. **Sort and Prioritize**: Sort by relevance, assign priority levels
9. **Return Results**: Structured response with statistics

**Return Structure**:
```json
{
  "matched_requirements": [
    {
      "category": "הרשות הארצית לכבאות והצלה",
      "paragraph_number": "5.1.1",
      "text": "Requirement text...",
      "relevance_score": 0.85,
      "matched_features": ["גז"],
      "source": "feature_mapping",
      "numeric_ranges": {...},
      "priority": "high"
    }
  ],
  "by_category": {...},
  "feature_coverage": ["גז", "מ\"ר", "תפוסה"],
  "user_profile": {...},
  "total_matches": 15,
  "summary": {
    "categories_count": 3,
    "priority_breakdown": {"high": 5, "medium": 7, "low": 3},
    "avg_relevance": 0.72,
    "business_profile": {...}
  }
}
```

## API Integration

### Questions API

The system dynamically generates questionnaire options based on `features.json`:

```python
def _create_feature_question_options(features_data) -> List[Dict[str, str]]
```

**Features**:
- Excludes mandatory fields (size, seating)
- Converts features to multiselect options
- Supports Hebrew labels and values

### Analysis API

The `/analyze` endpoint uses the matching algorithm to process user input:

```python
@api_blueprint.post("/analyze")
def analyze():
    # Process user input
    # Call match_requirements()
    # Return structured response
```

## Performance Optimizations

### Caching Strategy

1. **Rules Loader**: `@lru_cache(maxsize=1)` for data loading
2. **Feature Loading**: Cached per request in matching functions
3. **Regex Compilation**: Compiled patterns for numeric extraction

### Memory Management

1. **Lazy Loading**: Data loaded only when needed
2. **Efficient Data Structures**: Optimized for lookup performance
3. **Garbage Collection**: Proper cleanup of temporary data

## Error Handling

### Robust Error Handling

1. **File Loading**: Graceful fallback for missing files
2. **Data Validation**: Type checking and safe conversions
3. **Regex Processing**: Exception handling for malformed patterns
4. **JSON Serialization**: Safe handling of complex data types

### Logging and Debugging

1. **Warning Messages**: Non-critical errors logged as warnings
2. **Debug Information**: Detailed error context for troubleshooting
3. **Performance Metrics**: Timing and statistics for optimization

## Testing Strategy

### Unit Tests

1. **Input Normalization**: Test various input formats
2. **Range Extraction**: Test Hebrew text patterns
3. **Feature Matching**: Test dynamic feature loading
4. **Relevance Scoring**: Test scoring algorithms

### Integration Tests

1. **End-to-End**: Full API request/response cycle
2. **Data Loading**: Test with real processed data
3. **Performance**: Load testing with large datasets

## Configuration

### Environment Variables

- `FLASK_ENV`: Development/production mode
- `DEBUG`: Debug mode flag

### File Paths

- `app/data/processed/paragraphs.json`: Hierarchical document structure
- `app/data/processed/mappings.json`: Feature mappings
- `app/data/raw/features.json`: Dynamic feature definitions

## Future Enhancements

### Planned Improvements

1. **Machine Learning**: AI-powered relevance scoring
2. **Caching**: Redis for distributed caching
3. **Analytics**: User behavior tracking
4. **Internationalization**: Multi-language support

### Scalability Considerations

1. **Database**: Migration from JSON files to database
2. **Microservices**: Service decomposition for better scalability
3. **API Versioning**: Backward compatibility management

## Troubleshooting

### Common Issues

1. **500 Errors**: Check datetime imports and JSON serialization
2. **No Matches**: Verify feature mappings and user input
3. **Performance**: Monitor memory usage and caching effectiveness

### Debug Tools

1. **Test Scripts**: Standalone testing utilities
2. **Logging**: Detailed error messages and warnings
3. **API Testing**: Comprehensive endpoint testing

## Conclusion

The rules loader and matching algorithm provide a robust, scalable foundation for regulatory requirement matching. The system's use of design patterns, dynamic feature loading, and sophisticated matching algorithms ensures both maintainability and accuracy in regulatory compliance analysis.

The modular architecture allows for easy extension and modification while maintaining system stability and performance. The comprehensive error handling and testing strategies ensure reliable operation in production environments.
