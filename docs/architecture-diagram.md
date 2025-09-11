# System Architecture Diagram

## Data Flow Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PDF/DOCX      │───▶│   Parser         │───▶│  Processed Data │
│   Documents     │    │   (parse_rules)  │    │  (JSON files)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Response  │◀───│  Matching        │◀───│  Rules Loader   │
│   (JSON)        │    │  Algorithm       │    │  (Repository)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        ▲                        ▲
         │                        │                        │
         │                        │                        │
    ┌─────────┐              ┌─────────┐              ┌─────────┐
    │ Frontend│              │ User    │              │ Features│
    │ (React) │              │ Input   │              │ (JSON)  │
    └─────────┘              └─────────┘              └─────────┘
```

## Component Architecture

### Rules Loader (Repository Pattern)
```
┌─────────────────────────────────────┐
│           Rules Loader              │
├─────────────────────────────────────┤
│ @lru_cache(maxsize=1)               │
│ load_parser_data()                  │
├─────────────────────────────────────┤
│ get_paragraphs()                    │
│ get_mappings()                      │
│ get_paragraph_text()                │
└─────────────────────────────────────┘
```

### Matching Algorithm (Specification Pattern)
```
┌─────────────────────────────────────┐
│        Matching Algorithm           │
├─────────────────────────────────────┤
│ Input Normalization                 │
│ ├─ _normalize_user_input()          │
│ └─ Type conversion & validation     │
├─────────────────────────────────────┤
│ Numeric Range Extraction            │
│ ├─ _extract_numeric_ranges()        │
│ ├─ Hebrew regex patterns            │
│ └─ Min/Max/Exact value detection    │
├─────────────────────────────────────┤
│ Feature Matching                    │
│ ├─ _load_features_from_json()       │
│ ├─ _matches_user_profile()          │
│ └─ Dynamic feature loading          │
├─────────────────────────────────────┤
│ Relevance Scoring                   │
│ ├─ _assess_requirement_relevance()  │
│ ├─ Range-based scoring              │
│ └─ Feature-specific scoring         │
└─────────────────────────────────────┘
```

## Data Structures

### Paragraphs Structure
```
paragraphs.json
├── הרשות הארצית לכבאות והצלה
│   ├── 5
│   │   ├── text: "Main section..."
│   │   ├── 5.1
│   │   │   └── text: "Subsection..."
│   │   └── 5.2
│   └── 6
├── משרד הבריאות
│   └── ...
└── משטרת ישראל
    └── ...
```

### Mappings Structure
```
mappings.json
├── גז
│   ├── categories: {משרד הבריאות: [5.1, 5.2]}
│   └── paragraphs: [5.1, 5.2]
├── מצלמות
│   ├── categories: {משטרת ישראל: [3, 3.3]}
│   └── paragraphs: [3, 3.3]
└── עישון
    ├── categories: {משרד הבריאות: [4.1]}
    └── paragraphs: [4.1]
```

### Features Structure
```
features.json
├── גז
│   ├── categories: {משרד הבריאות: [גז, מערכת גז]}
│   └── keywords: [גז]
├── מ"ר
│   ├── search_all_categories: true
│   └── keywords: [regex patterns]
└── תפוסה
    ├── search_all_categories: true
    └── keywords: [regex patterns]
```

## API Layer

### Endpoints
```
┌─────────────────────────────────────┐
│              API Layer              │
├─────────────────────────────────────┤
│ GET  /health                        │
│ GET  /questions                     │
│ GET  /features                      │
│ POST /analyze                       │
│ GET  /preview-features              │
└─────────────────────────────────────┘
```

### Request/Response Flow
```
User Input → API Validation → Matching Algorithm → Rules Loader → Response
     │              │                │                    │
     ▼              ▼                ▼                    ▼
Frontend Form → JSON Schema → Business Logic → Data Access → JSON Response
```

## Design Patterns Used

### 1. Singleton Pattern
- **Location**: `rules_loader.py`
- **Implementation**: `@lru_cache(maxsize=1)`
- **Purpose**: Ensure data is loaded only once

### 2. Repository Pattern
- **Location**: `rules_loader.py`
- **Implementation**: Data access abstraction
- **Purpose**: Consistent data access interface

### 3. Specification Pattern
- **Location**: `matching.py`
- **Implementation**: Complex business rule evaluation
- **Purpose**: Flexible requirement matching logic

## Performance Optimizations

### Caching Strategy
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │───▶│   Rules Loader  │───▶│   File System   │
│   Startup       │    │   (Cached)      │    │   (JSON files)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌─────────────────┐
│   Request       │    │   Memory Cache  │
│   Processing    │    │   (LRU Cache)   │
└─────────────────┘    └─────────────────┘
```

### Memory Management
- **Lazy Loading**: Data loaded only when needed
- **Efficient Lookups**: Optimized data structures
- **Garbage Collection**: Proper cleanup of temporary data

## Error Handling

### Error Flow
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   Validation    │───▶│   Processing    │
│                 │    │   Layer         │    │   Layer         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Error         │    │   Error         │    │   Error         │
│   Response      │    │   Response      │    │   Response      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Error Types
- **Validation Errors**: Invalid input data
- **Processing Errors**: Algorithm failures
- **Data Errors**: File loading issues
- **Internal Errors**: Unexpected failures

## Testing Architecture

### Test Layers
```
┌─────────────────────────────────────┐
│           Integration Tests         │
├─────────────────────────────────────┤
│ Unit Tests                          │
│ ├─ Input Normalization              │
│ ├─ Range Extraction                 │
│ ├─ Feature Matching                 │
│ └─ Relevance Scoring                │
├─────────────────────────────────────┤
│ API Tests                           │
│ ├─ Endpoint Testing                 │
│ ├─ Request/Response Validation      │
│ └─ Error Handling                   │
└─────────────────────────────────────┘
```

## Deployment Architecture

### Development Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   Backend       │───▶│   Data Files    │
│   (React)       │    │   (Flask)       │    │   (JSON)        │
│   Port: 5173    │    │   Port: 5000    │    │   Local FS      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Production Considerations
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │───▶│   Application   │───▶│   Database      │
│   (Nginx)       │    │   Servers       │    │   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CDN           │    │   Redis Cache   │    │   File Storage  │
│   (Static)      │    │   (Sessions)    │    │   (S3/GCS)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```
