def parse_filter_string(filter_string):
    """
    Parse filter string into a dictionary of filter criteria

    Args:
        filter_string: Comma-separated string of filter criteria

    Returns:
        Dictionary of filter criteria
    """
    if not filter_string:
        return None

    # Split the string and create a dict of requirements
    parts = filter_string.strip().split(",")
    filter_dict = {}

    for part in parts:
        part = part.strip().lower()
        if part == "peeled":
            filter_dict["peeled"] = True
        elif part == "tail_off":
            filter_dict["tail_off"] = True
        elif part == "tail_on":
            filter_dict["tail_on"] = True
        elif part == "raw":
            filter_dict["is_raw"] = True
        elif part == "cooked":
            filter_dict["is_cooked"] = True
        elif part == "frozen":
            filter_dict["is_frozen"] = True
        elif part == "farm_raised":
            filter_dict["is_farm_raised"] = True
        elif part == "wild_caught":
            filter_dict["is_wild_caught"] = True

    return filter_dict


def filter_and_sort_products(results, attributes_to_filter=None, small_to_large=False):
    """
    Select products matching specific attributes and sort them by size

    Args:
        results: List of product results
        attributes_to_filter: Dict with attribute requirements (e.g., {'peeled': True, 'tail_off': True})
        small_to_large: If True, sort from smallest to largest, otherwise largest to smallest

    Returns:
        Filtered and sorted list of products
    """
    # Filter products based on attributes
    filtered_results = results

    if attributes_to_filter:
        filtered_results = []

        for result in results:
            # Check if product matches all required attributes
            match = True

            # Check preparation attributes
            prep_attrs = [p.lower() for p in result["prep_attributes"]]
            if "peeled" in attributes_to_filter and attributes_to_filter["peeled"]:
                if not any("peeled" in p for p in prep_attrs):
                    match = False

            if "tail_off" in attributes_to_filter and attributes_to_filter["tail_off"]:
                if not any("tail off" in p for p in prep_attrs):
                    match = False

            if "tail_on" in attributes_to_filter and attributes_to_filter["tail_on"]:
                if not any("tail on" in p for p in prep_attrs):
                    match = False

            # Check state attributes
            state_attrs = [s.lower() for s in result["state_attributes"]]
            if "is_raw" in attributes_to_filter and attributes_to_filter["is_raw"]:
                if not any("raw" in s for s in state_attrs):
                    match = False

            if (
                "is_cooked" in attributes_to_filter
                and attributes_to_filter["is_cooked"]
            ):
                if not any("cooked" in s for s in state_attrs):
                    match = False

            if (
                "is_frozen" in attributes_to_filter
                and attributes_to_filter["is_frozen"]
            ):
                if not any("frozen" in s for s in state_attrs):
                    match = False

            # Check source attributes
            source_attrs = [s.lower() for s in result["source_attributes"]]
            if (
                "is_farm_raised" in attributes_to_filter
                and attributes_to_filter["is_farm_raised"]
            ):
                if not any("farm raised" in s for s in source_attrs):
                    match = False

            if (
                "is_wild_caught" in attributes_to_filter
                and attributes_to_filter["is_wild_caught"]
            ):
                if not any("wild caught" in s for s in source_attrs):
                    match = False

            # If all attributes match, add to filtered results
            if match:
                filtered_results.append(result)

    # Filter out products with no size order
    filtered_results = [r for r in filtered_results if r.get("size_order") is not None]

    # Sort by size order
    if small_to_large:
        # For small to large, use negative of size_order (since our size_order is negative for large shrimp)
        sorted_results = sorted(filtered_results, key=lambda x: -x["size_order"])
    else:
        # For large to small, use size_order directly
        sorted_results = sorted(filtered_results, key=lambda x: x["size_order"])

    return sorted_results
