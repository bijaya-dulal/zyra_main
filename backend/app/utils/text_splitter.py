import re

FORMULA_PATTERN = re.compile(
    r'\$\$.*?\$\$|\$.*?\$|\\begin\{equation\}.*?\\end\{equation\}',
    re.DOTALL
)

HEADING_PATTERN = re.compile(r'^#{1,6}\s+.+$|^[A-Z][^.!?]*:$', re.MULTILINE)
LIST_PATTERN = re.compile(r'^\s*[\d\-\*\•]\s+', re.MULTILINE)
TABLE_PATTERN = re.compile(r'\|.*\|', re.MULTILINE)


def rough_token_count(text: str) -> int:
    """Approx token estimation (1 token ≈ 4 characters)."""
    return len(text) // 4


def split_sentences(text: str) -> list:
    """Clean sentence splitting that protects formulas & abbreviations."""
    placeholder = "<<<FORMULA>>>"
    formulas = []

    # Hide formulas
    def repl(m):
        formulas.append(m.group())
        return placeholder

    text = FORMULA_PATTERN.sub(repl, text)

    # Protect abbreviations
    replacements = {
        r'Dr\.': 'Dr<DOT>',
        r'Mr\.': 'Mr<DOT>',
        r'Mrs\.': 'Mrs<DOT>',
        r'Prof\.': 'Prof<DOT>',
        r'etc\.': 'etc<DOT>',
        r'i\.e\.': 'i<DOT>e<DOT>',
        r'e\.g\.': 'e<DOT>g<DOT>',
    }

    for k, v in replacements.items():
        text = re.sub(k, v, text)

    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

    # Restore text
    output = []
    idx = 0
    for p in parts:
        p = p.replace("<DOT>", ".")
        while placeholder in p and idx < len(formulas):
            p = p.replace(placeholder, formulas[idx], 1)
            idx += 1
        output.append(p.strip())

    return output
