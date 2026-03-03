import logging
import os
import sys

from ado_scraper.wit_scraper import WitScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


def main():
    logger.info("Starting ADO scraper")
    
    organization = os.environ.get("ADO_ORGANIZATION")
    project = os.environ.get("ADO_PROJECT")
    personal_access_token = os.environ.get("ADO_PAT")
    attachment_path = os.environ.get("ADO_ATTACHMENT_PATH")

    if not organization:
        logger.error("ADO_ORGANIZATION environment variable is not set")
        sys.exit(1)
    if not project:
        logger.error("ADO_PROJECT environment variable is not set")
        sys.exit(1)
    if not personal_access_token:
        logger.error("ADO_PAT environment variable is not set")
        sys.exit(1)
    if not attachment_path:
        logger.error("ADO_ATTACHMENT_PATH environment variable is not set")
        sys.exit(1)

    logger.info(f"Configuration: organization={organization}, project={project}")

    try:
        scraper = WitScraper(
            organization=organization,
            project=project,
            personal_access_token=personal_access_token,
        )

        raw_ids = os.environ.get("ADO_IDS", "")
        if raw_ids:
            ids = [int(x) for x in raw_ids.split(",") if x.strip()]
            logger.info(f"Using specified work item IDs: {ids}")
        else:
            ids = []
            logger.info("No work item IDs specified, will fetch all work items")

        work_items = scraper.fetch_work_items(ids=ids)
        logger.info(f"Processing {len(work_items['value'])} work items for attachments")

        for idx, wi in enumerate(work_items["value"], 1):
            work_item_id = wi.get("id", "unknown")
            logger.info(f"Processing work item {idx}/{len(work_items['value'])}: ID {work_item_id}")
            try:
                scraper.download_attachments(wi, attachment_path)
            except Exception as e:
                logger.error(
                    f"Failed to process attachments for work item {work_item_id}: {e}",
                    exc_info=True,
                )
                # Continue with next work item instead of failing completely
                continue

        logger.info("ADO scraper completed successfully")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
