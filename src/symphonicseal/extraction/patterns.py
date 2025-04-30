# Regular expression patterns for extracting information from product titles

# Patterns for detecting count ranges
COUNT_PATTERNS = {
    # 16/20 Count or 16-20 Count pattern
    "slash_count": r"(\d+)[-/](\d+)(?:\s+(?:Count|per|ct|Count/|count))",
    # 13 To 15 or 13 to 15 pattern
    "to_pattern": r"(\d+)\s+[Tt]o\s+(\d+)",
    # 21 to 25 Count pattern
    "to_count": r"(\d+)\s+[Tt]o\s+(\d+)\s+[Cc]ount",
    # 16/20 or 16-20 without 'Count' text
    "simple_range": r"(?<!\d)(\d+)[-/](\d+)(?!\d)",
    # Single number count like (10 Count)
    "single_count": r"\((\d+)[-\s]+(?:Count|per|ct)",
}


# Patterns for finding count ranges in text for entity annotation
def get_count_entity_patterns(count_range):
    """
    Get regex patterns for locating count entities in text

    Args:
        count_range: Tuple of (lower, upper) count range

    Returns:
        List of regex patterns to find this count range in text
    """
    lower, upper = count_range
    return [
        f"({lower}[-/]{upper})",  # 16-20, 16/20
        f"({lower})\\s+[Tt]o\\s+({upper})",  # 13 To 15, 13 to 15
        f"({lower})[-\\s]+(?:Count|per|ct)",  # 10 Count, 10 per
        f"\\(({lower}[-/]{upper})[^)]*\\)",  # (16-20 Count per lb)
        f"\\(({lower})[-\\s]+(?:Count|per|ct)[^)]*\\)",  # (10 Count per lb)
    ]
