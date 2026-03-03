import json
import logging
import os
from typing import List

from .ado_service import AdoService
from .file_utils import FileUtils

logger = logging.getLogger(__name__)


class WitScraper:
    def __init__(self, organization: str, project: str, personal_access_token: str):
        logger.info(
            f"Initializing WitScraper for organization: {organization}, project: {project}"
        )
        self.service = AdoService(organization, project, personal_access_token)

    def fetch_work_items(self, ids: List[int]):
        if len(ids) == 0:
            logger.info("No work item IDs provided, fetching all work item IDs")
            ids = self.service.get_work_item_ids()
        else:
            logger.info(f"Fetching {len(ids)} specified work items")

        batch_size = 200
        all_items = []
        total_batches = (len(ids) + batch_size - 1) // batch_size
        logger.info(f"Processing {len(ids)} work items in {total_batches} batches")

        for i in range(0, len(ids), batch_size):
            batch_num = (i // batch_size) + 1
            batch_ids = ids[i : i + batch_size]
            logger.debug(f"Processing batch {batch_num}/{total_batches} ({len(batch_ids)} items)")
            try:
                data = self.service.get_work_items(batch_ids)
                all_items.extend(data["value"])
                logger.debug(f"Batch {batch_num} completed successfully")
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {e}", exc_info=True)
                raise

        logger.info(f"Successfully fetched {len(all_items)} work items total")
        return {"value": all_items}

    def download_attachments(self, work_item, dest_folder: str):
        work_item_id = work_item.get("id", "unknown")
        logger.info(f"Processing attachments for work item ID: {work_item_id}")

        attachments = []
        if "relations" in work_item:
            for rel in work_item["relations"]:
                if rel.get("rel") == "AttachedFile":
                    attachments.append(rel)

        if not attachments:
            logger.info(f"No attachments found in work item {work_item_id}")
            return

        logger.info(f"Found {len(attachments)} attachment(s) in work item {work_item_id}")

        for idx, attachment in enumerate(attachments, 1):
            url = attachment["url"]
            attributes = attachment.get("attributes", {})
            name = attributes.get("name", "unnamed_attachment")
            logger.info(
                f"Downloading attachment {idx}/{len(attachments)}: {name} from work item {work_item_id}"
            )
            logger.debug(f"Attachment URL: {url}")

            try:
                out_path = os.path.join(dest_folder, name)
                self.service.download_url_to_path(url, out_path)
                logger.info(f"Successfully downloaded attachment: {out_path}")

                logger.debug(f"Extracting metadata for {out_path}")
                file_metadata = FileUtils.get_file_metadata(out_path)
                combined_metadata = {
                    "ado_attributes": attributes,
                    "file_metadata": file_metadata,
                }

                metadata_path = f"{out_path}.json"
                with open(metadata_path, "w") as f:
                    json.dump(combined_metadata, f, indent=4)
                logger.info(f"Saved metadata file: {metadata_path}")
            except Exception as e:
                logger.error(
                    f"Failed to download attachment {name} from work item {work_item_id}: {e}",
                    exc_info=True,
                )
                raise
