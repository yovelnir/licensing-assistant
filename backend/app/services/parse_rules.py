import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Iterable, Optional


# Add backend directory to Python path for app.* imports
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))


# -------------------------
# PDF / DOCX extraction
# -------------------------

def _read_pdf_with_fitz(path: Path) -> str:
    try:
        import fitz  # PyMuPDF
    except Exception:
        return ""
    text_parts: List[str] = []
    try:
        doc = fitz.open(str(path))
        try:
            for page in doc:
                # Prefer plain text layout
                txt = page.get_text("text") or ""
                text_parts.append(txt)
        finally:
            doc.close()
    except Exception:
        return ""
    return "\n".join(text_parts)


def _read_pdf_with_pdfplumber(path: Path) -> str:
    try:
        import pdfplumber
    except Exception:
        return ""
    chunks: List[str] = []
    try:
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                text = ""
                try:
                    text = page.extract_text(x_tolerance=1.2, y_tolerance=3) or ""
                except TypeError:
                    text = page.extract_text() or ""
                if not text:
                    try:
                        words = page.extract_words() or []
                        if words:
                            text = " ".join(w.get("text", "") for w in words)
                    except Exception:
                        pass
                chunks.append(text or "")
    except Exception:
        return ""
    return "\n".join(chunks)


def _read_pdf_with_pdfminer(path: Path) -> str:
    try:
        from pdfminer.high_level import extract_text as pdfminer_extract_text
    except Exception:
        return ""
    try:
        txt = pdfminer_extract_text(str(path)) or ""
    except Exception:
        return ""
    return txt


def read_pdf(path: Path) -> str:
    """
    Extract text from PDF with the following precedence:
      1) PyMuPDF (fitz) per page get_text("text") - PREFERRED for Hebrew chapter detection
      2) pdfplumber extract_text (fallback extract_words)
      3) pdfminer.six as last resort
    Returns concatenated pages separated by newlines.
    """
    # Try PyMuPDF first - it preserves Hebrew chapter headers best
    primary = _read_pdf_with_fitz(path)
    if primary:
        return primary  # Use PyMuPDF if available - it handles Hebrew chapters best
        
    # Fallback to pdfplumber
    secondary = _read_pdf_with_pdfplumber(path)
    if secondary:
        return secondary
        
    # Last resort: pdfminer
    miner = _read_pdf_with_pdfminer(path)
    if miner:
        return miner

    raise RuntimeError(
        "Failed to extract text from PDF. Please ensure PyMuPDF, pdfplumber or pdfminer.six is installed."
    )


def read_docx(path: Path) -> str:
    try:
        from docx import Document
    except Exception as exc:
        raise RuntimeError("python-docx not installed. pip install python-docx") from exc
    doc = Document(str(path))
    parts: List[str] = [p.text for p in doc.paragraphs]
    # include tables
    try:
        for table in getattr(doc, "tables", []):
            for row in table.rows:
                for cell in row.cells:
                    if cell.text:
                        parts.append(cell.text)
    except Exception:
        pass
    return "\n".join(parts)


# -------------------------
# Normalization helpers
# -------------------------

NUM_KEY_RE = re.compile(r"^\d+(?:\.\d+){0,19}$")

def _sorted_unique(numbers: Iterable[str]) -> List[str]:
    """Sort unique paragraph numbers by depth then lexicographically."""
    unique = sorted(set(str(n) for n in numbers))
    return sorted(unique, key=lambda n: (n.count('.'), n))


# -------------------------
# Canonicalization helpers
# -------------------------

def chapter_of(num: str) -> str:
    """Extract chapter number from a paragraph number."""
    return num.split(".")[0]


def canonicalize_num(raw_num: str, current_chapter: Optional[str]) -> str:
    """
    Canonicalize paragraph numbers relative to current chapter.
    
    Args:
        raw_num: Raw paragraph number from text
        current_chapter: Current chapter context (e.g., '4')
        
    Returns:
        Canonicalized number: raw if absolute, or prefixed with chapter if relative
        
    Examples:
        canonicalize_num('4', None) -> '4'
        canonicalize_num('1', '4') -> '4.1' 
        canonicalize_num('4.1', '4') -> '4.1'
    """
    if not current_chapter:
        return raw_num
    # already absolute under this chapter?
    if raw_num == current_chapter or raw_num.startswith(current_chapter + "."):
        return raw_num
    # otherwise, make it relative to current chapter
    return f"{current_chapter}.{raw_num}"


# Regex patterns for Hebrew document parsing
RE_CATEGORY = re.compile(r'^\s*פרק\s+(\d+)\s*(?:[-–—]\s*(.+?))?\s*$', re.U)  # Chapter headers
RE_NUM_START = re.compile(r'^\s*(\d+(?:\.\d+){0,19})(?=[\s\.\-\)])', re.U)  # Paragraph numbers


def ensure_node(tree: Dict, cat: str, num: str) -> Dict:
    """Ensure hierarchical node exists in tree."""
    if cat not in tree:
        tree[cat] = {}
    cur = tree[cat]
    path = []
    for part in num.split("."):
        path.append(part)
        key = ".".join(path)
        if key not in cur:
            cur[key] = {"text": ""}
        cur = cur[key]
    return cur


def add_text(tree: Dict, cat: str, num: str, text: str) -> None:
    """Add text to a paragraph node."""
    node = ensure_node(tree, cat, num)
    node["text"] = (node["text"] + (" " if node["text"] else "") + text).strip()


def parse_paragraphs(text: str) -> Dict[str, Any]:
    """
    Build hierarchical paragraph structure from normalized Hebrew text.
    
    Parses Hebrew documents with chapter headers (פרק N) and numbered paragraphs.
    Supports up to 20 levels of nesting (e.g., 1.2.3.4.5...).
    
    Args:
        text: Normalized document text
        
    Returns:
        Hierarchical structure: {category: {paragraph_num: {"text": content, nested_paragraphs}}}
        
    Example output:
        {
          "פרק 4": {
            "4": {"text": "Chapter content"},
            "4.1": {"text": "Paragraph content"}
          }
        }
    """
    if not text:
        return {}

    paragraphs: Dict[str, Dict] = {}
    current_cat: Optional[str] = None
    current_chapter: Optional[str] = None   # e.g., "4"
    current_num: Optional[str] = None

    # normalize lines: keep only non-empty
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    for ln in lines:
        # 1) explicit chapter header: "פרק 4 - משרד הבריאות"
        m_cat = RE_CATEGORY.match(ln)
        if m_cat:
            current_chapter = m_cat.group(1)         # "4"
            current_cat = (m_cat.group(2) or f"פרק {current_chapter}").strip()
            ensure_node(paragraphs, current_cat, current_chapter)
            current_num = current_chapter
            continue

        # 2) heading number at start
        m_start = RE_NUM_START.match(ln)
        if m_start:
            raw = m_start.group(1)                   # e.g., "1.1" or "4.6.3"
            num = canonicalize_num(raw, current_chapter)
            if current_cat is None:
                # fallback if file starts without "פרק ..."
                current_cat = f"פרק {chapter_of(num)}"
                current_chapter = chapter_of(num)
                ensure_node(paragraphs, current_cat, current_chapter)
            current_num = num
            add_text(paragraphs, current_cat, current_num, ln)
            continue

        # 3) plain text → append to current paragraph
        if current_cat and current_num:
            add_text(paragraphs, current_cat, current_num, ln)

    return paragraphs

def _cleanup_pdf_artifacts(text: str) -> str:
    """
    Clean up PDF extraction artifacts for better text processing.
    
    Removes:
    - Standalone page numbers
    - Dotted leaders (...)
    - Malformed Hebrew chapter headers
    
    Applied to both PDF and DOCX for consistency.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text with artifacts removed
    """
    cleaned_lines: List[str] = []
    for line in text.splitlines():
        if re.fullmatch(r"\s*\d+\s*", line):
            continue
        if re.search(r"\.{3,}\s*$", line):
            # drop lines that are mostly dotted leaders
            if re.fullmatch(r"\s*\.{3,}\s*", line):
                continue
            # trim trailing leaders
            line = re.sub(r"\.{3,}\s*$", "", line)
        
        # Fix malformed PDF chapter headers: "' פרק1 - '" -> "פרק 1 -"
        if 'פרק' in line:
            # Remove extra quotes
            line = line.strip("'\"")
            # Add space between פרק and number: "פרק1" -> "פרק 1"
            line = re.sub(r'פרק(\d+)', r'פרק \1', line)
            # Remove dotted leaders from chapter headers: "פרק 1 ......... הגדרות כלליות3" -> "פרק 1 - הגדרות כלליות"
            line = re.sub(r'(\d+)\s*\.{3,}\s*([^.\d]+?)[\d]*\s*$', r'\1 - \2', line)
            # Fix spacing around dashes and remove trailing quotes
            line = re.sub(r'(\d+)\s*-\s*[\'\"]*\s*$', r'\1 -', line)  # "פרק 1 - '" -> "פרק 1 -"
            line = re.sub(r'(\d+)\s*-\s*([^\s])', r'\1 - \2', line)   # "פרק 1 -text" -> "פרק 1 - text"
        
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def normalize(text: str) -> str:
    """
    Normalize extracted text for consistent processing.
    
    Normalization steps:
    1. Convert NBSP to regular spaces
    2. Unify different dash and quote characters
    3. Reflow hyphenated line breaks (Hebrew: "מ-\nשה" → "משה")
    4. Collapse multiple spaces and blank lines
    
    Args:
        text: Raw extracted text
        
    Returns:
        Normalized text ready for parsing
    """
    if not text:
        return ""

    s = text.replace("\u00A0", " ")
    # dashes
    s = s.replace("–", "-").replace("—", "-").replace("‑", "-").replace("_", " ")
    # quotes
    quote_map = {
        "“": '"', "”": '"', "„": '"', "‟": '"',
        "’": "'", "‘": "'", "‚": "'", "‛": "'",
    }
    for k, v in quote_map.items():
        s = s.replace(k, v)

    # Reflow hyphenated line breaks: hyphen or maqaf followed by newline
    s = re.sub(r"(?:-|־)\n(?=\S)", "", s)

    # Collapse spaces (preserve newlines)
    s = re.sub(r"[ \t\f\r\v]+", " ", s)
    lines = [ln.strip() for ln in s.splitlines()]
    s = "\n".join(lines)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s

def normalize_pipeline(raw_text: str) -> str:
    """
    Complete normalization pipeline as documented:
    1. Cleanup PDF artifacts
    2. Normalize text (character unification, reflow, whitespace)
    """
    if not raw_text:
        return ""
    
    # Step 1: Clean up PDF artifacts (applied to both PDF and DOCX for consistency)
    cleaned = _cleanup_pdf_artifacts(raw_text)
    
    # Step 2: Apply full normalization
    return normalize(cleaned)


# -------------------------
# Feature config loader
# -------------------------

def load_features_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("features.json must contain an object at the top level")
    return data


# -------------------------
# Verification utilities
# -------------------------


def _norm_text_compare(s: str) -> str:
    return " ".join((s or "").split())


def _collect_numeric_keys(paragraphs: Dict[str, Any]) -> Dict[str, List[str]]:
    per_cat: Dict[str, List[str]] = {}
    for cat, nodes in paragraphs.items():
        nums: List[str] = []
        stack: List[Tuple[str, Any]] = list(nodes.items())
        while stack:
            key, node = stack.pop()
            if isinstance(key, str) and NUM_KEY_RE.fullmatch(key):
                nums.append(key)
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "text":
                        continue
                    stack.append((k, v))
        per_cat[cat] = sorted(sorted(set(nums), key=lambda n: n), key=lambda n: len(n.split(".")))
    return per_cat


def _flatten_paragraphs(paragraphs: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """
    Flatten hierarchical paragraphs to searchable list.
    
    Returns tuples of (category, paragraph_number, text) for keyword matching.
    Categories are emitted in two forms when available:
    - Numeric chapter ID (e.g., '4') 
    - Chapter title (e.g., 'משרד הבריאות')
    
    This dual emission allows features.json to match by either identifier.
    
    Args:
        paragraphs: Hierarchical paragraph structure
        
    Returns:
        Flattened list of (category, number, text) tuples
    """
    rows: List[Tuple[str, str, str]] = []
    for chapter_id, nodes in paragraphs.items():
        if not isinstance(nodes, dict):
            continue
        chapter_title = str(nodes.get("text", "")).strip()
        stack: List[Tuple[str, Any]] = [(k, v) for k, v in nodes.items() if k != "text"]
        while stack:
            key, node = stack.pop()
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "text":
                        continue
                    stack.append((k, v))
                if isinstance(key, str) and NUM_KEY_RE.fullmatch(key):
                    txt = str(node.get("text", ""))
                    # emit numeric chapter id
                    rows.append((chapter_id, key, txt))
                    # emit chapter title alias
                    if chapter_title:
                        rows.append((chapter_title, key, txt))
    return rows


def _compile_keywords(keyword_items: Iterable[Any]) -> List[re.Pattern[str]]:
    """
    Compile keyword items into regex patterns for text matching.
    
    Supports two input formats:
    1. String literals: "exact text" (escaped, case-insensitive)
    2. Regex objects: {"regex": true, "pattern": "regex", "flags": ["I", "M"]}
    
    Args:
        keyword_items: Mixed iterable of strings and regex config dicts
        
    Returns:
        List of compiled regex patterns ready for text searching
    """
    patterns: List[re.Pattern[str]] = []
    for item in keyword_items:
        if isinstance(item, str):
            # Literal string - escape and compile with case-insensitive flag
            try:
                patterns.append(re.compile(re.escape(item), re.I))
            except re.error:
                continue
        elif isinstance(item, dict) and item.get("regex") is True and isinstance(item.get("pattern"), str):
            # Regex pattern with optional flags
            try:
                pattern = item["pattern"]
                flags = 0
                
                # Parse optional flags
                flag_names = item.get("flags", ["I"])  # Default to case-insensitive
                if isinstance(flag_names, list):
                    for flag_name in flag_names:
                        if isinstance(flag_name, str):
                            flag_name = flag_name.upper()
                            if hasattr(re, flag_name):
                                flags |= getattr(re, flag_name)
                
                # If no flags specified or parsing failed, default to case-insensitive
                if flags == 0:
                    flags = re.I
                    
                patterns.append(re.compile(pattern, flags))
            except (re.error, AttributeError, TypeError):
                continue
    return patterns


def build_mappings(paragraphs: Dict[str, Any], feature_keywords: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build feature mappings from paragraphs using flexible keyword matching.
    
    Supports multiple configuration formats:
    1. Category-specific: {"categories": {"cat1": [keywords], "cat2": [keywords]}}
    2. Single category: {"category": "cat_name", "keywords": [keywords]}  
    3. Search all categories: {"search_all_categories": true, "keywords": [keywords]}
    4. Legacy format: {"keywords": [keywords]} - searches all categories
    
    Keyword formats:
    - String literals: "exact text" (case-insensitive)
    - Regex patterns: {"regex": true, "pattern": "regex", "flags": ["I", "M"]}
    
    Args:
        paragraphs: Hierarchical paragraph structure by category
        feature_keywords: Feature configuration from features.json
        
    Returns:
        Feature mappings: {feature_name: {"categories": {...}, "paragraphs": [...]}}
    """
    rows = _flatten_paragraphs(paragraphs)
    by_cat: Dict[str, List[Tuple[str, str]]] = {}
    for cat, num, txt in rows:
        by_cat.setdefault(cat, []).append((num, txt))

    result: Dict[str, Any] = {}
    for feature_name, cfg in (feature_keywords or {}).items():
        entry: Dict[str, Any] = {"categories": {}, "paragraphs": []}

        if isinstance(cfg, dict) and isinstance(cfg.get("categories"), dict):
            # Format 1: Category-specific keyword mapping
            global_patterns = _compile_keywords(cfg.get("keywords", []))
            for cat_name, cat_keywords in cfg["categories"].items():
                patterns = _compile_keywords(cat_keywords) + global_patterns
                hits: List[str] = []
                for num, txt in by_cat.get(cat_name, []):
                    if any(p.search(txt) for p in patterns):
                        hits.append(num)
                sorted_hits = _sorted_unique(hits)
                if sorted_hits:
                    entry["categories"][cat_name] = sorted_hits
            union: List[str] = []
            for lst in entry["categories"].values():
                union.extend(lst)
            entry["paragraphs"] = _sorted_unique(union)

        elif isinstance(cfg, dict) and "category" in cfg and "keywords" in cfg:
            # Format 2: Single category targeting
            cat_name = cfg.get("category")
            patterns = _compile_keywords(cfg.get("keywords", []))
            hits: List[str] = []
            for num, txt in by_cat.get(cat_name, []):
                if any(p.search(txt) for p in patterns):
                    hits.append(num)
            sorted_hits = _sorted_unique(hits)
            if sorted_hits:
                entry["categories"][cat_name] = sorted_hits
            entry["paragraphs"] = _sorted_unique(hits)

        elif isinstance(cfg, dict) and (cfg.get("search_all_categories") is True or "keywords" in cfg):
            # Format 3 & 4: Search all categories (explicit flag or legacy fallback)
            patterns = _compile_keywords(cfg.get("keywords", []))
            union: List[str] = []
            for cat_name, items in by_cat.items():
                hits: List[str] = []
                for num, txt in items:
                    if any(p.search(txt) for p in patterns):
                        hits.append(num)
                sorted_hits = _sorted_unique(hits)
                if sorted_hits:
                    entry["categories"][cat_name] = sorted_hits
                    union.extend(sorted_hits)
            entry["paragraphs"] = _sorted_unique(union)

        result[feature_name] = entry

    return result
def compare_outputs(par_a: Dict[str, Any], map_a: Dict[str, Any], par_b: Dict[str, Any], map_b: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Compare two parser outputs for verification.
    
    Performs order-insensitive comparison:
    - Paragraph text: normalized whitespace comparison
    - Numeric keys: set equality per category  
    - Feature mappings: set comparison for lists
    
    Used for validating PDF vs DOCX parsing consistency.
    
    Args:
        par_a, par_b: Paragraph structures to compare
        map_a, map_b: Feature mappings to compare
        
    Returns:
        (is_equal, difference_summary)
    """

    # Compare category sets
    cats_a = set(par_a.keys())
    cats_b = set(par_b.keys())
    if cats_a != cats_b:
        only_a = sorted(cats_a - cats_b)
        only_b = sorted(cats_b - cats_a)
        return False, f"Category titles differ. only_in_A={only_a[:10]} only_in_B={only_b[:10]}"

    # Compare numeric keys per category
    nums_a = _collect_numeric_keys(par_a)
    nums_b = _collect_numeric_keys(par_b)
    for cat in sorted(cats_a):
        if nums_a.get(cat, []) != nums_b.get(cat, []):
            a_set = set(nums_a.get(cat, []))
            b_set = set(nums_b.get(cat, []))
            miss_a = sorted(b_set - a_set)[:10]
            miss_b = sorted(a_set - b_set)[:10]
            return False, f"Paragraph numbers differ in category '{cat}'. missing_in_A={miss_a} missing_in_B={miss_b}"

    # Compare text contents with whitespace normalization
    def walk_pairs(n1: Any, n2: Any, path: str) -> Tuple[bool, str]:
        if isinstance(n1, dict) and isinstance(n2, dict):
            keys = set(n1.keys()) | set(n2.keys())
            for k in sorted(keys):
                if k not in n1 or k not in n2:
                    return False, f"Key mismatch at {path}: {k}"
                if k == "text":
                    t1 = _norm_text_compare(n1.get("text", ""))
                    t2 = _norm_text_compare(n2.get("text", ""))
                    if t1 != t2:
                        return False, f"Text differs at {path}."
                else:
                    ok, msg = walk_pairs(n1[k], n2[k], path + f"/{k}")
                    if not ok:
                        return ok, msg
            return True, ""
        else:
            return True, ""

    ok, msg = walk_pairs(par_a, par_b, "paragraphs")
    if not ok:
        return False, msg

    # Compare mappings
    feats_a = set(map_a.keys())
    feats_b = set(map_b.keys())
    if feats_a != feats_b:
        return False, f"Feature keys differ. only_in_A={sorted(feats_a - feats_b)[:10]} only_in_B={sorted(feats_b - feats_a)[:10]}"

    def list_set(x: Any) -> List[str]:
        if not isinstance(x, list):
            return []
        return sorted(set(str(v) for v in x))

    for feat in sorted(feats_a):
        a = map_a[feat]
        b = map_b[feat]
        # compare union
        if list_set(a.get("paragraphs")) != list_set(b.get("paragraphs")):
            return False, f"Union paragraphs differ for feature '{feat}'"
        # per-category
        cats_a2 = set((a.get("categories") or {}).keys())
        cats_b2 = set((b.get("categories") or {}).keys())
        if cats_a2 != cats_b2:
            return False, f"Categories differ for feature '{feat}'"
        for cat in sorted(cats_a2):
            if list_set(a["categories"].get(cat)) != list_set(b["categories"].get(cat)):
                return False, f"Paragraph hits differ for feature '{feat}', category '{cat}'"

    return True, ""


# -------------------------
# Pipeline
# -------------------------

def run_pipeline(input_path: Path, features_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Execute complete document processing pipeline.
    
    Steps:
    1. Extract text from PDF/DOCX
    2. Normalize and clean text
    3. Parse hierarchical paragraph structure
    4. Build feature mappings from keywords
    
    Args:
        input_path: Path to PDF or DOCX file
        features_path: Path to features.json configuration
        
    Returns:
        (paragraphs_dict, mappings_dict)
    """
    ext = input_path.suffix.lower()
    if ext == ".pdf":
        raw = read_pdf(input_path)
        text = normalize_pipeline(raw)
        paragraphs = parse_paragraphs(text)
    elif ext == ".docx":
        raw = read_docx(input_path)
        text = normalize_pipeline(raw)
        paragraphs = parse_paragraphs(text)
    else:
        raise ValueError(f"Unsupported extension: {ext}")

    feature_keywords = load_features_json(features_path)
    mappings = build_mappings(paragraphs, feature_keywords)
    return paragraphs, mappings


def write_outputs(out_dir: Path, paragraphs: Dict[str, Any], mappings: Dict[str, Any]) -> None:
    """
    Write processing results to JSON files.
    
    Creates:
    - paragraphs.json: Hierarchical document structure
    - mappings.json: Feature-to-paragraph mappings
    
    Args:
        out_dir: Output directory path
        paragraphs: Parsed paragraph structure
        mappings: Feature mappings
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "paragraphs.json").write_text(
        json.dumps(paragraphs, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "mappings.json").write_text(
        json.dumps(mappings, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main(argv: List[str] | None = None) -> int:
    """
    Command-line interface for document processing pipeline.
    
    Usage:
        python parse_rules.py input.pdf features.json output_dir
        python parse_rules.py --verify-other input.docx input.pdf features.json output_dir
        
    Args:
        argv: Command line arguments (None = sys.argv)
        
    Returns:
        Exit code (0 = success, 1 = verification failed)
    """
    parser = argparse.ArgumentParser(description="Build paragraph index and feature mappings from a spec PDF/DOCX")
    parser.add_argument("input", help="Input PDF or DOCX path")
    parser.add_argument("features", help="features.json path")
    parser.add_argument("out_dir", help="Output directory")
    parser.add_argument("--verify-other", dest="verify_other", default=None, help="Other input (pdf/docx) to verify identical outputs")
    args = parser.parse_args(argv)

    input_path = Path(args.input).resolve()
    features_path = Path(args.features).resolve()
    out_dir = Path(args.out_dir).resolve()

    # Run primary pipeline
    paragraphs, mappings = run_pipeline(input_path, features_path)

    # If verify requested, run both and compare before writing
    if args.verify_other:
        other_path = Path(args.verify_other).resolve()
        paragraphs2, mappings2 = run_pipeline(other_path, features_path)
        same, diff = compare_outputs(paragraphs, mappings, paragraphs2, mappings2)
        if not same:
            sys.stderr.write(diff + "\n")
            return 1

    write_outputs(out_dir, paragraphs, mappings)
    print(f"Wrote: {out_dir / 'paragraphs.json'} and {out_dir / 'mappings.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())