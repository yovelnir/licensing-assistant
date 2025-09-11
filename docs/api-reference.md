# API Reference Documentation

## Overview

The licensing assistant API provides endpoints for regulatory requirement analysis and business compliance checking. The API follows RESTful principles and returns JSON responses.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently no authentication is required. All endpoints are publicly accessible.

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running and responsive.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK`: API is healthy
- `500 Internal Server Error`: API is not responding

---

### 2. Get Questions

**GET** `/questions`

Retrieve the dynamic questionnaire for business characteristics collection.

**Response:**
```json
{
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
    },
    {
      "name": "seats",
      "label": "מספר מקומות ישיבה / תפוסה",
      "type": "number", 
      "required": true,
      "min": 0,
      "max": 1000,
      "placeholder": "לדוגמה: 50",
      "description": "מספר לקוחות שיכולים לשבת במקום - נדרש לצורך סינון דרישות"
    },
    {
      "name": "attributes",
      "label": "מאפייני עסק נוספים",
      "type": "multiselect",
      "required": false,
      "options": [
        {
          "value": "גז",
          "label": "גז (Gas)"
        },
        {
          "value": "עישון", 
          "label": "עישון (Smoking)"
        },
        {
          "value": "מצלמות",
          "label": "מצלמות (CCTV)"
        }
      ],
      "description": "בחר את כל המאפיינים הרלוונטיים - מאפיינים נוספים המשפיעים על דרישות הרגולציה"
    }
  ],
  "metadata": {
    "questionnaire_version": "1.1",
    "required_fields": ["size_m2", "seats"],
    "description": "שאלון רישוי עסקים מסעדות לפי משימה טכנית",
    "instructions": "יש למלא לפחות את השדות הנדרשים (גודל ותפוסה) כדי לקבל ניתוח מדויק",
    "features_loaded": 3
  }
}
```

**Features:**
- **Dynamic Options**: Feature options loaded from `features.json`
- **Multilingual**: Hebrew labels with English translations
- **Validation**: Built-in min/max constraints
- **Accessibility**: Clear descriptions and placeholders

---

### 3. Get Features

**GET** `/features`

Retrieve available business features and their definitions.

**Response:**
```json
{
  "features": {
    "גז": {
      "categories": {
        "משרד הבריאות": ["גז", "מערכת גז", "בלוני גז"],
        "בטיחות אש": ["גז", "דליפת גז", "וסתי גז"]
      },
      "keywords": ["גז"]
    },
    "מצלמות": {
      "categories": {
        "משטרת ישראל": ["מצלמות", "טמ\"ס", "CCTV"]
      }
    },
    "עישון": {
      "category": "משרד הבריאות",
      "keywords": ["עישון", "שלטי עישון", "איסור עישון"]
    }
  },
  "metadata": {
    "total_features": 3,
    "categories": ["משרד הבריאות", "בטיחות אש", "משטרת ישראל"],
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

**Use Cases:**
- Frontend form generation
- Feature validation
- Dynamic UI building

---

### 4. Analyze Business

**POST** `/analyze`

Analyze business characteristics against regulatory requirements.

**Request Body:**
```json
{
  "size_m2": 120,
  "seats": 50,
  "attributes": ["גז", "עישון", "מצלמות"]
}
```

**Request Parameters:**
- `size_m2` (number, required): Business floor area in square meters
- `seats` (number, required): Number of seats/occupancy
- `attributes` (array, optional): List of business characteristics

**Response:**
```json
{
  "regulatory_analysis": {
    "matched_requirements": [
      {
        "category": "הרשות הארצית לכבאות והצלה",
        "paragraph_number": "5.1.1",
        "text": "חוק הרשות הארצית לכבאות והצלה, התשע\"ב., והתקנות על פיו",
        "relevance_score": 0.85,
        "matched_features": ["גז"],
        "source": "feature_mapping",
        "numeric_ranges": {
          "size_m2": {
            "min": 100,
            "max": 200,
            "exact": []
          },
          "occupancy": {
            "min": 30,
            "max": 80,
            "exact": [50]
          }
        },
        "priority": "high"
      }
    ],
    "by_category": {
      "הרשות הארצית לכבאות והצלה": [
        {
          "category": "הרשות הארצית לכבאות והצלה",
          "paragraph_number": "5.1.1",
          "text": "...",
          "relevance_score": 0.85,
          "matched_features": ["גז"],
          "source": "feature_mapping",
          "numeric_ranges": {...},
          "priority": "high"
        }
      ]
    },
    "feature_coverage": ["גז", "מ\"ר", "מצלמות", "עישון", "תפוסה"],
    "user_profile": {
      "size_m2": 120,
      "seats": 50,
      "attributes": ["גז", "עישון", "מצלמות"],
      "uses_gas": true,
      "serves_meat": false
    },
    "total_matches": 15,
    "summary": {
      "categories_count": 3,
      "priority_breakdown": {
        "high": 5,
        "medium": 7,
        "low": 3
      },
      "avg_relevance": 0.72,
      "business_profile": {
        "size_category": "large",
        "occupancy_category": "high",
        "special_requirements": true
      }
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "analysis_id": "analysis_12345"
}
```

**Response Fields:**
- `matched_requirements`: List of applicable regulatory requirements
- `by_category`: Requirements grouped by regulatory authority
- `feature_coverage`: Features that were matched
- `user_profile`: Normalized user input
- `total_matches`: Total number of matching requirements
- `summary`: Statistical summary and business profile

**Priority Levels:**
- `high`: Critical safety requirements or high relevance (≥0.8)
- `medium`: Important requirements (0.5-0.8)
- `low`: General requirements (<0.5)

---

### 5. Preview Features

**GET** `/preview-features`

Preview available features without full analysis.

**Response:**
```json
{
  "available_features": [
    {
      "name": "גז",
      "label": "גז (Gas)",
      "description": "Business uses gas equipment",
      "categories": ["משרד הבריאות", "בטיחות אש"]
    },
    {
      "name": "עישון",
      "label": "עישון (Smoking)", 
      "description": "Smoking-related requirements",
      "categories": ["משרד הבריאות"]
    },
    {
      "name": "מצלמות",
      "label": "מצלמות (CCTV)",
      "description": "Security camera requirements",
      "categories": ["משטרת ישראל"]
    }
  ],
  "mandatory_fields": ["size_m2", "seats"],
  "total_features": 3
}
```

## Error Responses

### Standard Error Format

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z",
  "details": {
    "field": "additional error details"
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Invalid input data
- `PROCESSING_ERROR`: Error during analysis
- `DATA_ERROR`: Error loading regulatory data
- `INTERNAL_ERROR`: Unexpected server error

### HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input data
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing rate limiting for production use.

## CORS

CORS is enabled for all origins. Configure appropriately for production.

## Data Formats

### Input Data Types

- **Numbers**: Integer or float values
- **Strings**: UTF-8 encoded text
- **Arrays**: JSON arrays
- **Booleans**: true/false values

### Output Data Types

- **Timestamps**: ISO 8601 format (UTC)
- **Numbers**: Float values with appropriate precision
- **Text**: UTF-8 encoded Hebrew and English text
- **IDs**: UUID format for analysis IDs

## Examples

### Complete Analysis Example

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "size_m2": 150,
    "seats": 60,
    "attributes": ["גז", "מצלמות"]
  }'
```

### Questions Retrieval Example

```bash
curl -X GET http://localhost:5000/questions
```

### Health Check Example

```bash
curl -X GET http://localhost:5000/health
```

## Testing

### Test Data

Use the following test data for development and testing:

```json
{
  "size_m2": 120,
  "seats": 50,
  "attributes": ["גז", "עישון", "מצלמות"]
}
```

### Expected Results

- Should return 15+ matching requirements
- Should include features: גז, מ"ר, מצלמות, עישון, תפוסה
- Should have high priority requirements for safety features

## Versioning

API versioning is handled through the `questionnaire_version` field in responses. Current version is `1.1`.

## Changelog

### Version 1.1
- Added dynamic feature loading from `features.json`
- Implemented numeric range matching
- Enhanced relevance scoring algorithm
- Added Hebrew text support

### Version 1.0
- Initial API implementation
- Basic requirement matching
- Static feature definitions
