import logging
import os
import sys
import traceback


def setup_logging(log_dir: str,
                  quiet: bool = False,
                  level=logging.INFO) -> logging.Logger:
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # Create a logger
    pid = os.getpid()
    logger = logging.getLogger(str(pid))
    logger.setLevel(level)

    # Check if the logger already has handlers to avoid duplicate logging
    if not logger.handlers:
        logger_format = '[%(asctime)s][%(name)s][%(levelname)s]: %(message)s'
        formatter = logging.Formatter(logger_format)

        if log_dir:
            # Add a file handler with the PID in the filename
            file_handler = logging.FileHandler(f"{log_dir}/{pid}.err")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        if not quiet:
            # Add a stream handler to print to stderr
            stream_handler = logging.StreamHandler(sys.stderr)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        # Prevent the logger from propagating messages to the root logger
        logger.propagate = False

    return logger


def format_exception(e):
    estr = "".join(traceback.format_exception(e))
    return f"\n```\n{estr}```\n\n"
