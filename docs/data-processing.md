## Data Processing Pipeline

This project implements a complete document processing pipeline that extracts Hebrew regulatory requirements from PDF/DOCX files and maps them to structured features using flexible keyword matching.

### Architecture Overview

The pipeline transforms raw regulatory documents into searchable, structured data through four main stages:

1. **Text Extraction**: Multi-library PDF/DOCX text extraction with Hebrew optimization
2. **Normalization**: Text cleaning and artifact removal  
3. **Hierarchical Parsing**: Chapter and paragraph structure extraction
4. **Feature Mapping**: Keyword-based content classification

### Source Data

**Input Files:**
- **Primary**: `backend/app/data/raw/18-07-2022_4.2A.pdf` - Hebrew restaurant licensing requirements
- **Secondary**: `backend/app/data/raw/18-07-2022_4.2A.docx` - Same content for format verification
- **Configuration**: `backend/app/data/raw/features.json` - Feature extraction rules

**Supported Formats:**
- PDF (PyMuPDF preferred, pdfplumber/pdfminer fallback)
- DOCX (python-docx with table support)

### Processing Pipeline

**Script**: `backend/app/services/parse_rules.py`  
**Usage**:
```powershell
cd backend
pipenv shell  # Use pipenv for dependency management
python app/services/parse_rules.py app/data/raw/18-07-2022_4.2A.pdf app/data/raw/features.json app/data/processed
```

**Verification Mode** (ensures PDF ≡ DOCX):
```powershell
python app/services/parse_rules.py app/data/raw/18-07-2022_4.2A.pdf app/data/raw/features.json app/data/processed --verify-other app/data/raw/18-07-2022_4.2A.docx
```

### Text Processing Features

#### 1. Multi-Library PDF Extraction
- **Primary**: PyMuPDF (fitz) - optimal for Hebrew chapter headers
- **Fallback**: pdfplumber with word-level extraction
- **Last Resort**: pdfminer.six

#### 2. Hebrew Text Normalization
- Character unification (NBSP→space, dash variants, quotes)
- Hyphenated line break reflow: `מ-\nשה` → `משה`
- PDF artifact removal (page numbers, dotted leaders)
- Chapter header repair: `פרק1` → `פרק 1`

#### 3. Hierarchical Document Parsing
- **Chapter Detection**: `פרק N [- title]` headers
- **Paragraph Numbers**: Supports up to 20 nesting levels (e.g., `1.2.3.4.5.6.7.8.9.10`)
- **Canonicalization**: Relative numbers prefixed with chapter context

### Output Schema

#### Paragraphs Structure (`paragraphs.json`)
```json
{
  "category_name": {
    "chapter_number": {
      "text": "chapter content",
      "sub.paragraph": {
        "text": "paragraph content",
        "sub.sub.paragraph": {
          "text": "nested content"
        }
      }
    }
  }
}
```

**Example:**
```json
{
  "הרשות הארצית לכבאות והצלה": {
    "5": {
      "text": "Chapter 5 overview text",
      "5.1": {
        "text": "Paragraph 5.1 content"  
      },
      "5.1.1": {
        "text": "Sub-paragraph 5.1.1 content"
      }
    }
  }
}
```

#### Feature Mappings (`mappings.json`)
```json
{
  "feature_name": {
    "categories": {
      "category_name": ["paragraph_numbers"]
    },
    "paragraphs": ["all_matching_paragraphs"]
  }
}
```

**Example:**
```json
{
  "עישון": {
    "categories": {
      "משרד הבריאות": ["4", "4.1", "4.5"]
    },
    "paragraphs": ["4", "4.1", "4.5"]
  }
}
```

### Feature Configuration (`features.json`)

#### 1. Category-Specific Keywords
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

#### 3. Global Search Mode
Search across all document categories:
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

#### 4. Legacy Format (Global Search)
Simple keyword-only format:
```json
{
  "emergency": {
    "keywords": ["חירום", "יציאת חירום", "חילוץ"]
  }
}
```

### Keyword Formats

#### Literal Strings
Case-insensitive exact matches:
```json
["כיבוי אש", "בטיחות אש", "גלאי עשן"]
```

#### Regex Patterns
Advanced pattern matching with configurable flags:
```json
[
  {
    "regex": true,
    "pattern": "\\d+\\s*מקומות",
    "flags": ["I", "U"]
  }
]
```

**Supported Regex Flags:**
- `I` - Case insensitive (default)
- `M` - Multiline mode
- `S` - Dotall mode (. matches newlines)  
- `U` - Unicode mode
- `X` - Verbose mode

### Advanced Examples

#### Complex Area Matching
```json
{
  "מ\"ר": {
    "search_all_categories": true,
    "keywords": [
      {"regex": true, "pattern": "[0-9]+\\s*מ\"ר"},
      {"regex": true, "pattern": "(?:עד|לפחות|מעל)\\s*\\d+[\\d.,]*\\s*(?:מ\\\"ר|מטר(?:ים)?\\s*מרובעים)"},
      {"regex": true, "pattern": "\\d+[\\d.,]*\\s*[-–־]\\s*\\d+[\\d.,]*\\s*(?:מ\\\"ר|מטר(?:ים)?\\s*מרובעים)"}
    ]
  }
}
```

#### Occupancy Detection
```json
{
  "תפוסה": {
    "search_all_categories": true,
    "keywords": [
      {"regex": true, "pattern": "\\d+\\s*איש"},
      {"regex": true, "pattern": "(?:עד|לפחות|מעל|יותר\\s*מ)\\s*\\d+\\s*איש"}
    ]
  }
}
```

### Data Integration

#### Rules Loader (`backend/app/services/rules_loader.py`)
- Loads processed `restaurant_rules.json` into memory
- Caches rules for efficient API access
- **Design Pattern**: Singleton/Factory for centralized rule management

#### Matching Service (`backend/app/services/matching.py`)
- Implements business logic matching algorithm
- Maps user attributes to applicable regulations
- **Design Pattern**: Specification pattern for complex rule evaluation

#### API Endpoints (`backend/app/api/routes.py`)
- `GET /api/questions`: Dynamic questionnaire generation
- `POST /api/analyze`: Attribute-to-requirement matching
- **Design Pattern**: Repository pattern for data access abstraction

### Performance Optimizations

1. **Caching**: In-memory rule caching via rules_loader
2. **Lazy Loading**: Feature mappings computed on-demand
3. **Efficient Regex**: Pre-compiled patterns with optimized flags
4. **Hierarchical Search**: Category-specific searches reduce scope

### Extension Points

1. **Additional Formats**: Extend with Word/HTML parsers
2. **Language Support**: Adapt regex patterns for other languages  
3. **Database Storage**: Replace JSON with PostgreSQL/MongoDB for scale
4. **ML Enhancement**: Add NER/classification for automatic feature detection
5. **Versioning**: Implement rule versioning for regulatory updates

### Verification & Testing

The pipeline includes comprehensive verification:
- **Format Consistency**: PDF vs DOCX output comparison
- **Text Normalization**: Whitespace-normalized content matching
- **Hierarchical Integrity**: Paragraph number set validation
- **Feature Mapping**: Order-independent list comparison

### Development Notes

- **Memory Usage**: Efficient for documents up to ~1000 pages
- **Hebrew Support**: Optimized for RTL text and Hebrew chapter headers
- **Error Handling**: Graceful fallbacks for missing libraries/malformed input
- **Deterministic**: Consistent output across runs and formats