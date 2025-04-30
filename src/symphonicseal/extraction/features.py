import re
import symphonicseal.extraction.patterns


def extract_features(title, size_keywords, attribute_keywords):
    """
    Extract features from product titles

    Args:
        title: Product title string
        size_keywords: List of size keywords to look for
        attribute_keywords: Dictionary of attribute keywords by category

    Returns:
        Tuple of (size_desc, count_range, attributes)
    """
    found_size = None
    for size in size_keywords:
        if size in title:
            found_size = size
            break

    # Handle special "Extra" cases
    if found_size is None and "Extra" in title:
        if "Small" in title:
            found_size = "Extra Small"
        elif "Large" in title:
            found_size = "Extra Large"
        elif "Jumbo" in title:
            found_size = "Extra Jumbo"
        elif "Colossal" in title:
            found_size = "Extra Colossal"

    # Extract count ranges using regex
    count_range = None

    # Try each pattern in order
    for (
        pattern_name,
        pattern,
    ) in symphonicseal.extraction.patterns.COUNT_PATTERNS.items():
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            lower = int(match.group(1))
            upper = int(match.group(2)) if len(match.groups()) > 1 else lower

            # Validate that this is likely a count range
            if (0 < lower < 150) and (0 < upper < 150) and (lower <= upper):
                count_range = (lower, upper)
                break

    # Extract other attributes
    attributes = {}
    for attr_type, keywords in attribute_keywords.items():
        for keyword in keywords:
            if keyword.lower() in title.lower():
                if attr_type not in attributes:
                    attributes[attr_type] = []
                attributes[attr_type].append(keyword)

    return found_size, count_range, attributes
