import logging
from typing import List

import requests

logger = logging.getLogger(__name__)


class AdoService:
    def __init__(self, organization: str, project: str, personal_access_token: str):
        self.organization = organization
        self.project = project
        self.pat = personal_access_token
        self.base_url = f"https://dev.azure.com/{organization}/{project}/_apis"
        self.session = requests.Session()
        self.session.auth = ("", self.pat)
        logger.info(
            f"Initialized AdoService for organization: {organization}, project: {project}"
        )

    def get_work_item_ids(self) -> List[int]:
        headers = {"Content-Type": "application/json"}
        params = {"api-version": "7.0"}
        wiql = "SELECT [System.Id] FROM WorkItems ORDER BY [System.Id] ASC"
        payload = {"query": wiql}
        logger.debug(f"Fetching work item IDs using WIQL query: {wiql}")
        try:
            response = self.session.post(
                f"{self.base_url}/wit/wiql", headers=headers, json=payload, params=params
            )
            response.raise_for_status()
            work_items = response.json().get("workItems", [])
            ids = [item["id"] for item in work_items]
            logger.info(f"Successfully retrieved {len(ids)} work item IDs")
            return ids
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch work item IDs: {e}", exc_info=True)
            raise

    def get_work_items(self, ids: List[int]):
        ids_str = ",".join(str(i) for i in ids)
        params = {"api-version": "7.0", "$expand": "relations", "ids": ids_str}
        headers = {"Content-Type": "application/json"}
        logger.debug(f"Fetching {len(ids)} work items: {ids_str[:100]}...")
        try:
            resp = self.session.get(
                f"{self.base_url}/wit/workitems", params=params, headers=headers
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"Successfully retrieved {len(data.get('value', []))} work items")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch work items: {e}", exc_info=True)
            raise

    def download_url_to_path(self, url: str, dest_path: str):
        params = {"api-version": "7.0"}
        logger.debug(f"Downloading file from {url} to {dest_path}")
        try:
            with self.session.get(url, params=params, stream=True) as r:
                r.raise_for_status()
                total_size = 0
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            total_size += len(chunk)
                logger.info(
                    f"Successfully downloaded file to {dest_path} ({total_size} bytes)"
                )
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download file from {url}: {e}", exc_info=True)
            raise
        except IOError as e:
            logger.error(f"Failed to write file to {dest_path}: {e}", exc_info=True)
            raise
