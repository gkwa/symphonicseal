def setup_attribute_classifications():
    """
    Set up attribute classifications for shrimp products

    Returns:
        Dictionary of attribute keywords by category
    """
    attribute_keywords = {
        "PREP": [
            "Peeled",
            "Deveined",
            "Tail On",
            "Tail Off",
            "Shell On",
            "Shell Off",
            "Easy Peel",
            "Head On",
            "Head Off",
            "Butterflied",
        ],
        "SOURCE": [
            "Farm Raised",
            "Wild Caught",
            "Gulf",
            "Pacific",
            "Atlantic",
            "White",
            "Pink",
            "Brown",
            "Black Tiger",
            "Key West",
            "Coconut",
        ],
        "STATE": ["Raw", "Cooked", "Previously Frozen", "Fresh", "Frozen"],
    }

    return attribute_keywords


def normalize_attributes(attributes):
    """
    Normalize attributes to fix capitalization issues

    Args:
        attributes: Dictionary of attributes by category

    Returns:
        Dictionary of normalized attributes by category
    """
    normalized = {"PREP": [], "SOURCE": [], "STATE": []}

    # Define standardized versions for common attributes
    standardization = {
        "tail on": "Tail On",
        "tail off": "Tail Off",
        "peeled": "Peeled",
        "deveined": "Deveined",
        "fresh": "Fresh",
        "frozen": "Frozen",
        "raw": "Raw",
        "cooked": "Cooked",
        "wild caught": "Wild Caught",
        "farm raised": "Farm Raised",
        "easy peel": "Easy Peel",
        "previously frozen": "Previously Frozen",
    }

    # Normalize each attribute type
    for attr_type, attr_list in attributes.items():
        seen = set()  # Track attributes we've already added

        for attr in attr_list:
            # Standardize using the mapping, or keep original if not in mapping
            attr_lower = attr.lower()
            if attr_lower in standardization:
                normalized_attr = standardization[attr_lower]
            else:
                normalized_attr = attr

            # Only add if we haven't seen this normalized version yet
            if normalized_attr.lower() not in seen:
                normalized[attr_type].append(normalized_attr)
                seen.add(normalized_attr.lower())

    return normalized
