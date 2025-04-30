import pandas


def save_results_to_csv(results, filename="shrimp_data.csv"):
    """
    Convert the results to a pandas DataFrame and save to CSV

    Args:
        results: List of product results
        filename: CSV file path to save to

    Returns:
        DataFrame of results
    """
    # Define the columns for our spreadsheet
    columns = [
        "title",
        "standardized_size",
        "detected_size",
        "detected_count",
        "size_order",
        "tail_on",
        "tail_off",
        "peeled",
        "deveined",
        "easy_peel",
        "shell_on",
        "head_on",
        "is_farm_raised",
        "is_wild_caught",
        "source_location",
        "is_frozen",
        "is_raw",
        "is_cooked",
        "is_fresh",
    ]

    # Create a list to hold our row data
    rows = []

    # Process each result
    for result in results:
        # Create a dictionary for this row
        row = {col: None for col in columns}

        # Fill in the basic fields
        row["title"] = result["title"]
        row["standardized_size"] = result["standardized_size"]
        row["detected_size"] = result["detected_size"]
        row["detected_count"] = result["detected_count"]
        row["size_order"] = result["size_order"]

        # Process preparation attributes
        prep_attrs = [p.lower() for p in result["prep_attributes"]]
        row["tail_on"] = any("tail on" in p for p in prep_attrs)
        row["tail_off"] = any("tail off" in p for p in prep_attrs)
        row["peeled"] = any("peeled" in p for p in prep_attrs)
        row["deveined"] = any("deveined" in p for p in prep_attrs)
        row["easy_peel"] = any("easy peel" in p for p in prep_attrs)
        row["shell_on"] = any("shell on" in p for p in prep_attrs)
        row["head_on"] = any("head on" in p for p in prep_attrs)

        # Process source attributes
        source_attrs = [s.lower() for s in result["source_attributes"]]
        row["is_farm_raised"] = any("farm raised" in s for s in source_attrs)
        row["is_wild_caught"] = any("wild caught" in s for s in source_attrs)

        # Extract source location (Gulf, Pacific, etc.)
        source_locations = []
        for s in result["source_attributes"]:
            if s.lower() not in ["farm raised", "wild caught"]:
                source_locations.append(s)
        row["source_location"] = (
            ", ".join(source_locations) if source_locations else None
        )

        # Process state attributes
        state_attrs = [s.lower() for s in result["state_attributes"]]
        row["is_frozen"] = any("frozen" in s for s in state_attrs)
        row["is_raw"] = any("raw" in s for s in state_attrs)
        row["is_cooked"] = any("cooked" in s for s in state_attrs)
        row["is_fresh"] = any("fresh" in s for s in state_attrs)

        # Add the row to our list
        rows.append(row)

    # Create a DataFrame
    df = pandas.DataFrame(rows, columns=columns)

    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"\nData saved to {filename}")

    return df


def save_skipped_titles(skipped_titles, filename="skipped_titles.csv"):
    """
    Save skipped titles to CSV file

    Args:
        skipped_titles: List of skipped titles
        filename: CSV file path to save to
    """
    # Create a DataFrame for skipped titles
    skipped_df = pandas.DataFrame(
        {"order": range(1, len(skipped_titles) + 1), "title": skipped_titles}
    )

    # Save to CSV
    skipped_df.to_csv(filename, index=False)
    print(f"Saved {len(skipped_titles)} skipped titles to '{filename}'")
