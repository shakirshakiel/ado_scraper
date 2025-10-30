import os

from ado_scraper.wit_scraper import WitScraper


def main():
    scraper = WitScraper(
        organization=os.environ.get("ADO_ORGANIZATION"),
        project=os.environ.get("ADO_PROJECT"),
        personal_access_token=os.environ.get("ADO_PAT"),
    )
    raw_ids = os.environ.get("ADO_IDS", "")
    ids = [int(x) for x in raw_ids.split(",") if x.strip()]
    work_items = scraper.fetch_work_items(ids=ids)
    for wi in work_items["value"]:
        print(f"Processing work item ID: {wi.get('id')}")
        scraper.download_attachments(wi, os.environ.get("ADO_ATTACHMENT_PATH"))


if __name__ == "__main__":
    main()
