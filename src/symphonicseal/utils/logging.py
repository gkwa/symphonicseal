import logging
import os


def get_log_level(verbosity):
    """
    Convert verbosity level to logging level

    Args:
        verbosity: Integer representing verbosity level (0-3)

    Returns:
        Logging level constant from the logging module
    """
    if verbosity == 0:
        return logging.WARNING
    elif verbosity == 1:
        return logging.INFO
    else:  # verbosity >= 2
        return logging.DEBUG


def configure_logging(log_level, show_model_paths=False):
    """
    Configure logging with the specified log level

    Args:
        log_level: Logging level constant from the logging module
        show_model_paths: Whether to show model paths in debug logs
    """
    # Create a custom formatter
    if show_model_paths:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(pathname)s:%(lineno)d] - %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add a console handler with the formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # Log to file as well if LOG_FILE environment variable is set
    log_file = os.environ.get("LOG_FILE")
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)
