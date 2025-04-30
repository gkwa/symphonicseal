import re
import symphonicseal.classification.attributes
import symphonicseal.classification.size


def extract_size_info(doc, size_mapping, count_to_size):
    """
    Process entities and extract size ordering

    Args:
        doc: spaCy Doc object
        size_mapping: Dictionary mapping size names to count ranges
        count_to_size: Dictionary mapping count ranges to size names

    Returns:
        Tuple of (standardized_size, size_entity, count_entity, size_order, attributes)
    """
    size_entity = None
    count_entity = None
    attributes = {"PREP": [], "SOURCE": [], "STATE": []}

    # Extract entities
    for ent in doc.ents:
        if ent.label_ == "SIZE":
            size_entity = ent.text
        elif ent.label_ == "COUNT":
            count_entity = ent.text
        elif ent.label_ in ["PREP", "SOURCE", "STATE"]:
            attributes[ent.label_].append(ent.text)

    # Normalize attributes to fix capitalization issues
    attributes = symphonicseal.classification.attributes.normalize_attributes(
        attributes
    )

    # Process count entity for size ordering
    size_order = None
    detected_count = None

    if count_entity:
        # Parse the count range
        match = re.search(r"(\d+)[-/](\d+)", count_entity)
        if match:
            lower = int(match.group(1))
            upper = int(match.group(2))
            detected_count = (lower, upper)

            # Use average for ordering
            avg_count = (lower + upper) / 2

            # Lower average count means larger shrimp
            # We invert the value for proper ordering (lower is bigger)
            size_order = -avg_count

    # If no count entity, use size entity for ordering
    if size_order is None and size_entity:
        # Assign numeric order based on size descriptions
        # Larger sizes get higher values (more negative = larger shrimp)
        size_order_map = symphonicseal.classification.size.get_size_order_map()

        # Find closest match in size order map
        for size_name, order_value in size_order_map.items():
            if size_name.lower() in size_entity.lower():
                size_order = order_value
                break

        # Default order if no match found
        if size_order is None:
            size_order = -999  # Put at the end of ordering

    # For standardization, use either the size name or try to map from count
    standardized_size = size_entity

    # If we have a count range but no size name, try to find a standard size
    if not standardized_size and detected_count:
        for (range_min, range_max), size in count_to_size.items():
            # Check if the detected range overlaps with this standard range
            if detected_count[0] <= range_max and detected_count[1] >= range_min:
                standardized_size = size
                break

    return standardized_size, size_entity, count_entity, size_order, attributes


def process_title(title, ner_model, size_mapping, count_to_size):
    """
    Process a title with NER and size ordering

    Args:
        title: Product title string
        ner_model: Trained spaCy NER model
        size_mapping: Dictionary mapping size names to count ranges
        count_to_size: Dictionary mapping count ranges to size names

    Returns:
        Tuple of (standardized_size, size_entity, count_entity, size_order, attributes)
    """
    doc = ner_model(title)
    return extract_size_info(doc, size_mapping, count_to_size)


def process_titles(titles, ner_model, size_mapping, count_to_size):
    """
    Process all titles and extract information

    Args:
        titles: List of product titles
        ner_model: Trained spaCy NER model
        size_mapping: Dictionary mapping size names to count ranges
        count_to_size: Dictionary mapping count ranges to size names

    Returns:
        List of processed results
    """
    results = []

    for title in titles:
        standardized_size, size_entity, count_entity, size_order, attributes = (
            process_title(title, ner_model, size_mapping, count_to_size)
        )

        results.append(
            {
                "title": title,
                "detected_size": size_entity,
                "detected_count": count_entity,
                "standardized_size": standardized_size,
                "size_order": size_order,
                "prep_attributes": attributes["PREP"],
                "source_attributes": attributes["SOURCE"],
                "state_attributes": attributes["STATE"],
            }
        )

    return results


def process_sample_titles(sample_titles, ner_model, size_mapping, count_to_size):
    """
    Process and display results for sample titles

    Args:
        sample_titles: List of sample product titles
        ner_model: Trained spaCy NER model
        size_mapping: Dictionary mapping size names to count ranges
        count_to_size: Dictionary mapping count ranges to size names
    """
    for i, title in enumerate(sample_titles):
        doc = ner_model(title)

        # Display entities found
        entities = [(ent.text, ent.label_) for ent in doc.ents]

        # Extract standardized size
        standardized_size, size_entity, count_entity, size_order, attributes = (
            extract_size_info(doc, size_mapping, count_to_size)
        )

        print(f"\nTitle {i + 1}: {title}")
        print(f"Entities: {entities}")
        print(f"Extracted size: {standardized_size}")
        if size_order is not None:
            print(f"Size Order Value: {size_order}")

        if attributes["PREP"] or attributes["SOURCE"] or attributes["STATE"]:
            print("Attributes:")
            if attributes["PREP"]:
                print(f"  Preparation: {', '.join(attributes['PREP'])}")
            if attributes["SOURCE"]:
                print(f"  Source: {', '.join(attributes['SOURCE'])}")
            if attributes["STATE"]:
                print(f"  State: {', '.join(attributes['STATE'])}")
