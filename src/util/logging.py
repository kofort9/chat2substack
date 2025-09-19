"""Logging utilities for chat2substack pipeline."""

import logging
import sys
from typing import Dict, Any


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('chat2substack')


def log_run_stats(logger: logging.Logger, stats: Dict[str, Any]) -> None:
    """Log run statistics in a structured format."""
    logger.info("=== Run Statistics ===")
    for key, value in stats.items():
        logger.info(f"{key}: {value}")
    logger.info("=====================")


def log_redaction_stats(logger: logging.Logger, stats: Dict[str, int]) -> None:
    """Log redaction statistics."""
    logger.info("=== Redaction Statistics ===")
    for pattern, count in stats.items():
        if count > 0:
            logger.info(f"{pattern}: {count} redactions")
    logger.info("============================")
