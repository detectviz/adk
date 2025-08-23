"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import logging
import sys

# Set up structured logging for GCP
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure handler to output JSON logs that work well with GCP
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)


def log_structured(severity, message, **kwargs):
    """
    Log a structured message compatible with Google Cloud Logging.

    Args:
        severity: The log severity ('INFO', 'ERROR', 'WARNING', 'DEBUG')
        message: The main log message
        **kwargs: Additional key-value pairs to include in the log
    """
    log_entry = {"severity": severity, "message": message, **kwargs}

    json_entry = json.dumps(log_entry)
    if severity == "ERROR":
        logger.error(json_entry)
    elif severity == "WARNING":
        logger.warning(json_entry)
    elif severity == "DEBUG":
        logger.debug(json_entry)
    else:
        logger.info(json_entry)


# Convenience methods
def info(message, **kwargs):
    """Log an INFO level message"""
    log_structured("INFO", message, **kwargs)


def error(message, **kwargs):
    """Log an ERROR level message"""
    log_structured("ERROR", message, **kwargs)


def warning(message, **kwargs):
    """Log a WARNING level message"""
    log_structured("WARNING", message, **kwargs)


def debug(message, **kwargs):
    """Log a DEBUG level message"""
    log_structured("DEBUG", message, **kwargs)
