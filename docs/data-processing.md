## Data Processing

This project demonstrates a minimal, end-to-end pipeline that converts raw restaurant licensing requirements into a structured format and maps business attributes to regulatory rules.

### Source Data
- Input: a small curated subset of restaurant requirements authored as YAML: `backend/app/data/raw/restaurant_rules.yaml`.
- Rationale: Instead of parsing the full PDF/Word, we extracted a representative subset to validate the architecture and mapping.

### Processor
- Script: `backend/app/services/parse_rules.py`
- Action: reads the source PDF/DOCX and writes normalized JSON to `backend/app/data/processed/restaurant_rules.json`.
- Run:
  ```powershell
  cd backend
  pip install -r requirements.txt
  python app/services/parse_rules.py app/data/raw/18-07-2022_4.2A.pdf app/data/raw/features.json app/data/processed
  ```

### Keyword Mapping and Regex Support

The processor supports flexible keyword matching for feature extraction via `features.json`. Keywords can be specified in two formats:

#### 1. Literal String Keywords
Simple strings are matched literally (case-insensitive):
```json
{
  "fire_safety": {
    "keywords": ["כיבוי אש", "בטיחות אש", "גלאי עשן"]
  }
}
```

#### 2. Regex Pattern Keywords  
For advanced pattern matching, use regex format:
```json
{
  "seating_capacity": {
    "keywords": [
      "מקומות ישיבה",
      {
        "regex": true,
        "pattern": "\\d+\\s*מקומות",
        "flags": ["I", "U"]
      }
    ]
  }
}
```

**Supported regex flags:**
- `I` - Case insensitive (default)
- `M` - Multiline mode
- `S` - Dotall mode (. matches newlines)  
- `U` - Unicode mode
- `X` - Verbose mode

**Feature configuration formats:**

#### 1. Category-Specific Mapping
Target specific document sections with tailored keywords:
```json
{
  "kitchen_equipment": {
    "keywords": ["ציוד מטבח"],
    "categories": {
      "פרק 3": ["גז", {"regex": true, "pattern": "חשמל\\s+\\d+V"}],
      "פרק 4": ["מקרר", "תנור"]
    }
  }
}
```

#### 2. Single Category Targeting
Search within one specific category:
```json
{
  "health_regulations": {
    "category": "משרד הבריאות",
    "keywords": ["תברואה", "היגיינה", "עישון"]
  }
}
```

#### 3. Search All Categories
Automatically search across all available categories using `search_all_categories: true`:
```json
{
  "safety_general": {
    "search_all_categories": true,
    "keywords": [
      "בטיחות",
      "סכנה", 
      {"regex": true, "pattern": "אישור\\s*(?:משטרה|כבאות|בריאות)"}
    ]
  }
}
```

#### 4. Legacy Global Search  
Simple keyword-only format (searches all categories by default):
```json
{
  "emergency": {
    "keywords": ["חירום", "יציאת חירום", "חילוץ"]
  }
}

### Schema (Normalized)
Each rule becomes a JSON object:
```json
{
  "id": "string",
  "category": "fire_safety | safety | sanitation | zoning | other",
  "title": "string",
  "description": "string",
  "priority": "high | medium | low",
  "conditions": {
    "min_size_m2": 101,
    "max_size_m2": 100,
    "min_seats": 51,
    "max_seats": null,
    "uses_gas": true,
    "serves_meat": false
  }
}
```

### Hierarchical parsing (sections → rules → conditions)

The extractor follows a hierarchical structure supporting **deep nesting up to 20 levels**:

- Category (Section): numeric like `3`
- Rule (Subsection): numeric like `3.1` 
- Sub-rule: numeric like `3.1.2`
- **Deep nesting**: supports complex structures like `2.7.2.7.1` or `5.5.6.5.6.10`

**Real-world depth support:**
- **Previous limit**: 4 levels (e.g., `1.2.3.4`)
- **Enhanced support**: Up to 20 levels (e.g., `2.2.1.2.1.11.2.1.11.8.2.1.11.8.2`)
- **Common usage**: Most documents use 4-8 levels, with legal documents reaching 15+ levels

For every rule we output a single object with aggregated conditions from all of its sub-subsections in the `conditions` field, and preserve source details in `meta.sub_conditions`. Aggregation:

- min_size_m2/min_seats: maximum of detected mins
- max_size_m2/max_seats: minimum of detected maxes
- uses_gas/serves_meat: true if any block requires it; null if unspecified

Each rule includes:

```
{
  id,
  category,
  title,
  description,
  priority,
  conditions,
  meta: {
    auto_extracted, needs_review,
    hierarchy: { category: {code,title}, rule: {code,title} },
    sub_conditions: [ { code, title, text, conditions } ]
  }
}
```

### Attribute → Requirement Mapping
- Implemented in `backend/app/services/matching.py` using a Specification-style predicate:
  - Numeric ranges: `size_m2`, `seats` must satisfy optional min/max bounds.
  - Booleans match when specified: `uses_gas`, `serves_meat`.
- Loader caches rules in memory: `backend/app/services/rules_loader.py`.

### API Exposure
- `GET /api/questions`: returns the questionnaire needed to collect business attributes (size, seats, gas usage, meat serving).
- `POST /api/analyze`: accepts answers and returns `matched_rules` and `by_category` groupings.

### Notes
- The same pipeline can be extended to parse PDFs/Word directly (e.g., `pdfplumber`, `python-docx`) and to enrich conditions.
- For larger datasets, store processed rules in a database and version them.
