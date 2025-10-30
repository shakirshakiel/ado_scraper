from typing import List

import requests


class AdoService:
    def __init__(self, organization: str, project: str, personal_access_token: str):
        self.organization = organization
        self.project = project
        self.pat = personal_access_token
        self.base_url = f"https://dev.azure.com/{organization}/{project}/_apis"
        self.session = requests.Session()
        self.session.auth = ("", self.pat)

    def get_work_item_ids(self) -> List[int]:
        headers = {"Content-Type": "application/json"}
        params = {"api-version": "7.0"}
        wiql = "SELECT [System.Id] FROM WorkItems ORDER BY [System.Id] ASC"
        payload = {"query": wiql}
        response = self.session.post(
            f"{self.base_url}/wit/wiql", headers=headers, json=payload, params=params
        )
        response.raise_for_status()
        return [item["id"] for item in response.json().get("workItems", [])]

    def get_work_items(self, ids: List[int]):
        ids_str = ",".join(str(i) for i in ids)
        params = {"api-version": "7.0", "$expand": "relations", "ids": ids_str}
        headers = {"Content-Type": "application/json"}
        resp = self.session.get(
            f"{self.base_url}/wit/workitems", params=params, headers=headers
        )
        resp.raise_for_status()
        return resp.json()

    def download_url_to_path(self, url: str, dest_path: str):
        params = {"api-version": "7.0"}
        with self.session.get(url, params=params, stream=True) as r:
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
