import re
from typing import List
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Matches LaTeX/math formulas: block ($$...$$), inline ($...$), and equation environments
FORMULA_PATTERN = re.compile(
    r'\$\$.*?\$\$|\$.*?\$|\\begin\{equation\}.*?\\end\{equation\}',
    re.DOTALL
)

# Matches headings: Markdown (#), ALL CAPS with colon, Title Case with colon
HEADING_PATTERN = re.compile(
    r'^#{1,6}\s+.+$'                              # Markdown: # Heading
    r'|^([A-Z][A-Z0-9\s\-]{2,}):\s*$'             # ALL CAPS: INTRODUCTION:
    r'|^([A-Z][a-z]+(\s+[A-Z][a-z]+)*):\s*$',     # Title Case: Key Points:
    re.MULTILINE
)

# Matches list bullets: digits, -, *, and common Unicode bullets (•, ‣, ▪, ●)
LIST_PATTERN = re.compile(
    r'^\s*[\d\-\*\u2022\u2023\u25AA\u25CF]\s+', 
    re.MULTILINE
)

# Matches Markdown table rows: lines with at least two pipe-separated columns
TABLE_PATTERN = re.compile(
    r'^\s*\|(?:[^\|]+\|){2,}.*$', 
    re.MULTILINE
)


def rough_token_count(text: str) -> int:
    """
    Approximate token estimation (1 token ≈ 4 characters).
    
    For production use, consider using tiktoken for accurate counts:
        import tiktoken
        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(enc.encode(text))
    
    Args:
        text: Input text to count tokens for
        
    Returns:
        Approximate token count
        
    Raises:
        TypeError: If text is not a string
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected string, got {type(text).__name__}")
    
    if not text:
        return 0
    
    return len(text) // 4


def split_sentences(text: str) -> List[str]:
    """
    Clean sentence splitting that protects formulas & abbreviations.
    
    Handles:
    - LaTeX formulas ($$...$$, $...$)
    - Common abbreviations (Dr., Prof., etc.)
    - Academic citations (i.e., e.g., cf.)
    
    Args:
        text: Input text to split into sentences
        
    Returns:
        List of sentence strings (empty sentences filtered out)
        
    Raises:
        TypeError: If text is not a string
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected string, got {type(text).__name__}")
    
    if not text or not text.strip():
        return []
    
    try:
        placeholder = "<<<FORMULA>>>"
        formulas = []

        # Step 1: Hide formulas to protect them from sentence splitting
        def replace_formula(match):
            formulas.append(match.group())
            return placeholder

        text = FORMULA_PATTERN.sub(replace_formula, text)

        # Step 2: Protect common abbreviations
        abbreviations = {
            r'Dr\.': 'Dr<DOT>',
            r'Mr\.': 'Mr<DOT>',
            r'Mrs\.': 'Mrs<DOT>',
            r'Ms\.': 'Ms<DOT>',          # Added
            r'Prof\.': 'Prof<DOT>',
            r'etc\.': 'etc<DOT>',
            r'i\.e\.': 'i<DOT>e<DOT>',
            r'e\.g\.': 'e<DOT>g<DOT>',
            r'vs\.': 'vs<DOT>',          # Added (versus)
            r'cf\.': 'cf<DOT>',          # Added (compare/see)
            r'Fig\.': 'Fig<DOT>',        # Added (Figure)
            r'Eq\.': 'Eq<DOT>',          # Added (Equation)
            r'No\.': 'No<DOT>',          # Added (Number)
            r'pp\.': 'pp<DOT>',          # Added (pages)
            r'Vol\.': 'Vol<DOT>',        # Added (Volume)
        }

        for pattern, replacement in abbreviations.items():
            text = re.sub(pattern, replacement, text)

        # Step 3: Split on sentence boundaries
        # Pattern: period/exclamation/question mark + space + capital letter
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

        # Step 4: Restore abbreviations and formulas
        output = []
        formula_idx = 0
        
        for sentence in sentences:
            # Restore dots in abbreviations
            sentence = sentence.replace("<DOT>", ".")
            
            # Restore formulas in order
            while placeholder in sentence and formula_idx < len(formulas):
                sentence = sentence.replace(placeholder, formulas[formula_idx], 1)
                formula_idx += 1
            
            # Only add non-empty sentences
            cleaned = sentence.strip()
            if cleaned:
                output.append(cleaned)

        return output
    
    except Exception as e:
        logger.error(f"Error splitting sentences: {e}", exc_info=True)
        # Fallback: return original text as single sentence
        return [text.strip()] if text.strip() else []


def extract_heading_text(text: str) -> str:
    """
    Extract clean heading text without markdown symbols or trailing colons.
    
    Examples:
        "# Introduction" → "Introduction"
        "CHAPTER 1:" → "CHAPTER 1"
        "Key Points:" → "Key Points"
    
    Args:
        text: Heading text to clean
        
    Returns:
        Cleaned heading text
    """
    if not text:
        return ""
    
    # Remove markdown symbols
    text = re.sub(r'^#{1,6}\s+', '', text)
    # Remove trailing colon and whitespace
    text = re.sub(r':\s*$', '', text)
    return text.strip()

