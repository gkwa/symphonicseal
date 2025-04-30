import re
import symphonicseal.extraction.features
import symphonicseal.extraction.patterns


def create_training_data(titles, size_keywords, attribute_keywords):
    """
    Create training data for NER with multiple entity types and track skipped titles

    Args:
        titles: List of product titles
        size_keywords: List of size keywords to look for
        attribute_keywords: Dictionary of attribute keywords by category

    Returns:
        Tuple of (training_data, skipped_titles)
    """
    training_data = []
    skipped_titles = []  # Track titles that are skipped

    for title in titles:
        size_desc, count_range, attributes = (
            symphonicseal.extraction.features.extract_features(
                title, size_keywords, attribute_keywords
            )
        )

        # Skip titles where we couldn't extract features
        if size_desc is None and count_range is None and not attributes:
            skipped_titles.append(title)
            continue

        # Create entity annotations
        entities = []

        # Add size description entity
        if size_desc:
            start = title.find(size_desc)
            end = start + len(size_desc)
            if start >= 0:
                entities.append((start, end, "SIZE"))

        # Add count range entity - also handle "X To Y" format
        if count_range:
            # Find the count range in the text - handle more patterns
            patterns = symphonicseal.extraction.patterns.get_count_entity_patterns(
                count_range
            )

            for pattern in patterns:
                match = re.search(pattern, title)
                if match:
                    # If we found a match within parentheses, extract just the numbers
                    count_text = match.group(1)
                    # Find the position of the count text in the title
                    start = title.find(count_text)
                    end = start + len(count_text)
                    if start >= 0:
                        entities.append((start, end, "COUNT"))
                        break

        # Add attribute entities
        for attr_type, attr_list in attributes.items():
            for attr in attr_list:
                # Case insensitive search
                title_lower = title.lower()
                attr_lower = attr.lower()
                start_index = title_lower.find(attr_lower)

                if start_index >= 0:
                    # Use the original title to get correct capitalization
                    end_index = start_index + len(attr)

                    # Check for overlapping entities before adding
                    overlapping = False
                    for existing_start, existing_end, _ in entities:
                        # Check if this entity overlaps with any existing entity
                        if start_index <= existing_end and end_index >= existing_start:
                            overlapping = True
                            break

                    # Only add if not overlapping
                    if not overlapping:
                        entities.append((start_index, end_index, attr_type))

        # Only add examples with entities
        if entities:
            training_data.append((title, {"entities": entities}))

    return training_data, skipped_titles
