import json
import os
from typing import List

from .ado_service import AdoService


class WitScraper:
    def __init__(self, organization: str, project: str, personal_access_token: str):
        self.service = AdoService(organization, project, personal_access_token)

    def fetch_work_items(self, ids: List[int]):
        if len(ids) == 0:
            ids = self.service.get_work_item_ids()

        batch_size = 200
        all_items = []
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i : i + batch_size]
            data = self.service.get_work_items(batch_ids)
            all_items.extend(data["value"])
        return {"value": all_items}

    def download_attachments(self, work_item, dest_folder: str):
        attachments = []
        if "relations" in work_item:
            for rel in work_item["relations"]:
                if rel.get("rel") == "AttachedFile":
                    attachments.append(rel)

        if not attachments:
            print("No attachments found in this work item.")
            return

        for attachment in attachments:
            url = attachment["url"]
            attributes = attachment.get("attributes", {})
            name = attributes.get("name", "unnamed_attachment")
            print(f"Downloading {name} from {url} ...")
            out_path = os.path.join(dest_folder, name)
            self.service.download_url_to_path(url, out_path)
            print(f"Saved: {out_path}")

            with open(f"{out_path}.json", "w") as f:
                json.dump(attributes, f, indent=4)
            print(f"Saved: {out_path}.json")
