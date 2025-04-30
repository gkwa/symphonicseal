import random
import time
import pathlib
import logging
import spacy
import platformdirs
import os
import sys


def get_model_path(model_name="shrimp_model"):
    """
    Get the platform-appropriate path for storing the model

    Args:
        model_name: Name of the model directory

    Returns:
        Path object for the model directory
    """
    # Get user data directory for this application
    app_data_dir = platformdirs.user_data_dir(
        appname="symphonicseal", appauthor="symphonicseal"
    )

    # Create models subdirectory
    models_dir = os.path.join(app_data_dir, "models")

    # Create the directory if it doesn't exist
    os.makedirs(models_dir, exist_ok=True)

    # Return the path for this specific model
    model_path = pathlib.Path(os.path.join(models_dir, model_name))

    # Always log model path at debug level
    logging.debug("Model path: %s", model_path)

    return model_path


def get_ner_model(
    training_data, model_dir="shrimp_model", force_retrain=False, iterations=20
):
    """
    Train or load a spaCy NER model

    Args:
        training_data: List of training examples
        model_dir: Name of model directory (not full path)
        force_retrain: Whether to force retraining even if model exists
        iterations: Number of training iterations

    Returns:
        Trained spaCy NER model
    """
    # Get platform-appropriate path for the model
    model_path = get_model_path(model_dir)

    # Check if model already exists and we're not forcing retraining
    if model_path.exists() and not force_retrain:
        logging.info("Loading existing model from %s", model_path)

        try:
            nlp = spacy.load(model_path)

            # Validate the model has the required components
            if "ner" in nlp.pipe_names:
                return nlp
            else:
                logging.warning(
                    "Loaded model doesn't have NER component. Retraining..."
                )
        except Exception as e:
            logging.error("Error loading model: %s", e)
            logging.info("Retraining model...")
    else:
        if force_retrain:
            logging.info("Force retraining requested. Training new model...")
        else:
            logging.info("Model directory doesn't exist. Training new model...")

    # Send a brief message to stderr indicating training is starting
    print("Training NER model - this may take a moment...", file=sys.stderr, flush=True)

    # Train a new model
    logging.info("Training NER model with %d examples...", len(training_data))
    start_time = time.time()

    # Create a blank spaCy model
    nlp = spacy.blank("en")

    # Create the NER component
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")

    # Add entity labels
    for _, annotations in training_data:
        for _, _, label in annotations.get("entities", []):
            ner.add_label(label)

    # Start training
    nlp.initialize()

    # Get batch sizes - using a generator function instead of compounding
    def get_batch_sizes():
        start, stop, compound = 4.0, 32.0, 1.001
        curr = start
        while curr < stop:
            yield curr
            curr = curr * compound

    # Generate batch sizes
    batch_sizes = list(get_batch_sizes())

    # Training loop
    losses = {}
    for iteration in range(iterations):
        random.shuffle(training_data)
        batches = []

        # Print progress indicator to stderr
        if (iteration + 1) % 5 == 0 or iteration == 0:
            print(
                f"Training progress: {iteration + 1}/{iterations} iterations",
                file=sys.stderr,
                flush=True,
            )

        # Create minibatches manually
        examples_list = list(training_data)
        for i in range(
            0,
            len(examples_list),
            int(batch_sizes[min(iteration, len(batch_sizes) - 1)]),
        ):
            batch_end = min(
                i + int(batch_sizes[min(iteration, len(batch_sizes) - 1)]),
                len(examples_list),
            )
            batches.append(examples_list[i:batch_end])

        for batch in batches:
            examples = []

            for text, annotations in batch:
                doc = nlp.make_doc(text)
                example = spacy.training.example.Example.from_dict(doc, annotations)
                examples.append(example)

            nlp.update(examples, drop=0.5, losses=losses)

        if logging.getLogger().getEffectiveLevel() <= logging.INFO:
            print(f"Iteration {iteration + 1}, Loss: {losses.get('ner', 0):.4f}")

    end_time = time.time()
    training_time = end_time - start_time

    print(
        f"Training completed in {training_time:.2f} seconds",
        file=sys.stderr,
        flush=True,
    )
    logging.info("Training completed in %.2f seconds", training_time)

    # Save the model
    if not model_path.exists():
        model_path.mkdir(parents=True, exist_ok=True)

    nlp.to_disk(model_path)
    logging.info("Model saved to %s", model_path)

    return nlp
