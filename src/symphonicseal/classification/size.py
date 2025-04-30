def setup_size_classifications():
    """
    Set up size classifications for shrimp

    Returns:
        Tuple of (size_mapping, count_to_size)
    """
    # Size classification with count ranges
    size_mapping = {
        "Extra Colossal": "U/10",  # under 10 per pound
        "Super Colossal": "U/12",  # under 12 per pound
        "Colossal": "U/15",  # under 15 per pound
        "Extra Jumbo": "16/20",  # 16-20 per pound
        "Jumbo": "21/25",  # 21-25 per pound
        "Extra Large": "26/30",  # 26-30 per pound
        "Large": "31/40",  # 31-40 per pound
        "Medium": "41/50",  # 41-50 per pound
        "Small": "51/60",  # 51-60 per pound
        "Extra Small": "61/70",  # 61-70 per pound
        "Tiny": "71/90",  # 71-90 per pound
        "Miniature": "91/110",  # 91-110 per pound
    }

    # Mapping from count ranges to size categories
    count_to_size = {
        (0, 10): "Extra Colossal",
        (10, 12): "Super Colossal",
        (12, 15): "Colossal",
        (16, 20): "Extra Jumbo",
        (21, 25): "Jumbo",
        (26, 30): "Extra Large",
        (31, 40): "Large",
        (41, 50): "Medium",
        (51, 60): "Small",
        (61, 70): "Extra Small",
        (71, 90): "Tiny",
        (91, 110): "Miniature",
        (111, 150): "Miniature",
        (151, 999): "Miniature",  # Anything larger is just "Miniature"
    }

    return size_mapping, count_to_size


def get_size_order_map():
    """
    Get mapping from size to order value for sorting

    Returns:
        Dictionary mapping size names to order values (lower = larger shrimp)
    """
    return {
        "Extra Colossal": -5,
        "Super Colossal": -10,
        "Colossal": -15,
        "Extra Jumbo": -20,
        "Jumbo": -25,
        "Extra Large": -30,
        "Large": -40,
        "Medium": -50,
        "Small": -60,
        "Extra Small": -70,
        "Tiny": -90,
        "Miniature": -110,
    }
