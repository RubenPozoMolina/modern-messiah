import argparse
import logging
from pathlib import Path
from mm.modern_messiah import ModernMessiah

def setup_logging(log_level=logging.INFO):
    """Configure logging for the application."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger('modern_messiah')

def main(config_path):

    if not config_path:
        logger.error("No configuration file provided.")
        return
    
    config_file = Path(config_path)
    if not config_file.exists():
        logger.error(f"Configuration file not found: {config_path}")
        return
        
    logger.info(f"Starting book generation with config: {config_path}")
    try:
        modern_messiah = ModernMessiah(config_path, logger = logger)
        logger.info("Initialized ModernMessiah instance")
        
        modern_messiah.write_book()
        logger.info("Book generation completed successfully")
    except Exception as exc:
        logger.exception(f"Error during book generation: {str(exc)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a book using the specified configuration file."
    )
    parser.add_argument(
        "--config-path",
        help="Path to the configuration file",
        dest="config_path"
    )
    parser.add_argument(
        "--log-level",
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        default="INFO",
        dest="log_level"
    )

    args = parser.parse_args()

    # Convert string log level to logging constant
    numeric_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logger = setup_logging(numeric_level)

    try:
        main(args.config_path)
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}")
        exit(1)