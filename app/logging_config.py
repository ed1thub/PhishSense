import logging


def configure_logging(level: str) -> None:
    normalized = (level or "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, normalized, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
