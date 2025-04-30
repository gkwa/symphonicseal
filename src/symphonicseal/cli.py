import argparse
import sys
import logging

import symphonicseal.data.loader
import symphonicseal.data.exporter
import symphonicseal.classification.size
import symphonicseal.classification.attributes
import symphonicseal.models.training
import symphonicseal.models.ner
import symphonicseal.processing.processor
import symphonicseal.processing.filter
import symphonicseal.utils.logging


def setup_logging(verbosity):
    """
    Set up logging with appropriate verbosity level

    Args:
        verbosity: Integer representing verbosity level (0-3)
    """
    log_level = symphonicseal.utils.logging.get_log_level(verbosity)
    show_models = verbosity >= 2  # Show model paths at debug level (verbosity >= 2)

    symphonicseal.utils.logging.configure_logging(log_level, show_models)

    logging.debug("Logging initialized with verbosity level %d", verbosity)


def parse_args():
    parser = argparse.ArgumentParser(description="Shrimp Size Extraction Tool")

    parser.add_argument(
        "--input", default="shrimp.txt", help="Input file with shrimp product titles"
    )

    parser.add_argument(
        "--force-retrain",
        action="store_true",
        help="Force retraining even if model exists",
    )

    parser.add_argument(
        "--model-dir", default="shrimp_model", help="Directory to save/load model"
    )

    parser.add_argument("--output", default="shrimp_data.csv", help="Output CSV file")

    parser.add_argument(
        "--filter-output",
        default="filtered_shrimp.csv",
        help="Output CSV for filtered results",
    )

    parser.add_argument(
        "--filter",
        default="peeled,tail_off,raw",
        help="Filter criteria (comma-separated)",
    )

    parser.add_argument(
        "--url",
        default="https://raw.githubusercontent.com/gkwa/symphonicseal/712b8dab19ad4aaa8c313f65d71de9545d2c1673/shrimp.txt",
        help="URL to load data from if input file doesn't exist (supports http://, https://, file://)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (can be specified multiple times, e.g. -vvv)",
    )

    return parser.parse_args()


def main() -> None:
    # Parse command-line arguments
    args = parse_args()

    # Set up logging with appropriate verbosity
    setup_logging(args.verbose)

    logging.info("Starting symphonicseal with verbosity level %d", args.verbose)
    logging.debug("Command line arguments: %s", vars(args))

    # Load data
    logging.info("Loading data from input file or URL")
    data = symphonicseal.data.loader.load_data(args.input, args.url)

    if not data:
        logging.error("No data could be loaded. Exiting.")
        sys.exit(1)

    logging.info("Total number of product titles: %d", len(data))

    if logging.getLogger().getEffectiveLevel() <= logging.INFO:
        print("First few product titles:")
        for i, title in enumerate(data[:5]):
            print(f"{i + 1}. {title}")

    # Set up classifications
    logging.info("Setting up size and attribute classifications")
    size_mapping, count_to_size = (
        symphonicseal.classification.size.setup_size_classifications()
    )

    attribute_keywords = (
        symphonicseal.classification.attributes.setup_attribute_classifications()
    )

    if logging.getLogger().getEffectiveLevel() <= logging.INFO:
        print("\nSize mapping reference:")
        for size, count_range in size_mapping.items():
            print(f"{size}: {count_range}")

    # Create training data
    logging.info("Creating training data")
    size_keywords = list(size_mapping.keys())
    training_data, skipped_titles = symphonicseal.models.training.create_training_data(
        data, size_keywords, attribute_keywords
    )

    logging.info("Created %d training examples", len(training_data))
    logging.info("Skipped %d titles due to no recognized features", len(skipped_titles))

    # Save skipped titles to CSV
    symphonicseal.data.exporter.save_skipped_titles(
        skipped_titles, "skipped_titles.csv"
    )

    # Display all of the skipped titles if in debug mode
    if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
        print("\nAll skipped titles:")
        for i, title in enumerate(skipped_titles):
            print(f"{i + 1}. {title}")

    # Display a few training examples if available
    if training_data and logging.getLogger().getEffectiveLevel() <= logging.INFO:
        print("\nSample training examples:")
        for i, (text, annot) in enumerate(training_data[: min(3, len(training_data))]):
            print(f"Example {i + 1}:")
            print(f"Text: {text}")
            print(f"Entities: {annot['entities']}")
            print()
    elif not training_data:
        logging.error("No training examples were created!")
        sys.exit(1)

    # Get the model - either load existing or train new
    logging.info("Getting NER model (loading or training)")
    ner_model = symphonicseal.models.ner.get_ner_model(
        training_data, model_dir=args.model_dir, force_retrain=args.force_retrain
    )

    # Test the model on sample data if not in quiet mode
    if logging.getLogger().getEffectiveLevel() <= logging.INFO:
        print("\nTesting the model on sample data:")
        sample_titles = data[:5] if len(data) >= 5 else data
        symphonicseal.processing.processor.process_sample_titles(
            sample_titles, ner_model, size_mapping, count_to_size
        )

    # Process all titles and store results
    logging.info("Processing all titles")
    all_results = symphonicseal.processing.processor.process_titles(
        data, ner_model, size_mapping, count_to_size
    )

    # Save all results to CSV
    logging.info("Saving results to CSV file: %s", args.output)
    symphonicseal.data.exporter.save_results_to_csv(all_results, args.output)

    # Apply filters if specified
    filter_dict = symphonicseal.processing.filter.parse_filter_string(args.filter)

    if filter_dict:
        logging.info("Applying filters: %s", args.filter)

        filter_names = []
        for key in filter_dict:
            if key == "peeled":
                filter_names.append("Peeled")
            elif key == "tail_off":
                filter_names.append("Tail Off")
            elif key == "tail_on":
                filter_names.append("Tail On")
            elif key == "is_raw":
                filter_names.append("Raw")
            elif key == "is_cooked":
                filter_names.append("Cooked")
            elif key == "is_frozen":
                filter_names.append("Frozen")
            elif key == "is_farm_raised":
                filter_names.append("Farm Raised")
            elif key == "is_wild_caught":
                filter_names.append("Wild Caught")

        if logging.getLogger().getEffectiveLevel() <= logging.INFO:
            print(
                f"\n=== Special Filter: {', '.join(filter_names)} Shrimp (Small to Large) ==="
            )

        filtered_results = symphonicseal.processing.filter.filter_and_sort_products(
            all_results, attributes_to_filter=filter_dict, small_to_large=True
        )

        # Display the filtered results if not in quiet mode
        if logging.getLogger().getEffectiveLevel() <= logging.INFO:
            print(
                f"Found {len(filtered_results)} products matching the criteria ({', '.join(filter_names)})"
            )

            if filtered_results:
                # Display all filtered results
                for i, result in enumerate(filtered_results):
                    print(f"{i + 1}. {result['title']}")
                    print(f"   Size: {result['standardized_size'] or 'Unknown'}")
                    # Size order is negative, so we need to negate it for small-to-large display
                    print(f"   Size Order Value: {-result['size_order']}")
                    # Show the matching attributes that we filtered on
                    print(f"   Preparation: {', '.join(result['prep_attributes'])}")
                    print(f"   State: {', '.join(result['state_attributes'])}")
                    print()

        # Save filtered results to a separate CSV
        if filtered_results:
            logging.info("Saving filtered results to: %s", args.filter_output)
            symphonicseal.data.exporter.save_results_to_csv(
                filtered_results, args.filter_output
            )

            if logging.getLogger().getEffectiveLevel() <= logging.INFO:
                print(
                    f"Filtered results saved to '{args.filter_output}' for spreadsheet analysis."
                )
        else:
            logging.info("No products matched the filter criteria")

            if logging.getLogger().getEffectiveLevel() <= logging.INFO:
                print("No products matched the filter criteria.")

    # Conclusion
    if logging.getLogger().getEffectiveLevel() <= logging.INFO:
        print("\n=== Conclusion ===")
        print(
            "This NER model can extract shrimp sizes and additional attributes from product titles."
        )
        print(
            "It provides a size ordering mechanism to sort products from largest to smallest shrimp."
        )
        print(
            "The model also extracts preparation methods, sources, and product states."
        )
        print("All data has been saved to CSV files for spreadsheet analysis.")
        print(f"  - Main results: {args.output}")
        print("  - Skipped titles: skipped_titles.csv")
        if filter_dict and filtered_results:
            print(f"  - Filtered results: {args.filter_output}")

    logging.info("Symphonicseal processing completed successfully")
