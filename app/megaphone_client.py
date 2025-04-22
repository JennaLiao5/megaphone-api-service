import os
import requests
from dotenv import load_dotenv
from app.schemas.campaigns import CampaignCreate, CampaignUpdate
from ratelimit import limits, sleep_and_retry

load_dotenv()

API_TOKEN = os.getenv("MEGAPHONE_API_TOKEN")
BASE_URL = os.getenv("MEGAPHONE_BASE_URL")
ORGANIZATION_ID = os.getenv("MEGAPHONE_ORG_ID")

headers = {
    "Authorization": f'Token token="{API_TOKEN}"',
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# --- Rate-limited requests wrapper ---
@sleep_and_retry
@limits(calls=60, period=60)
def safe_request(method: str, url: str, **kwargs):
    response = requests.request(method, url, headers=headers, **kwargs)
    response.raise_for_status()
    return response


def camelize_dict(d: dict) -> dict:
    def camelize(s):
        parts = s.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])
    return {camelize(k): v for k, v in d.items()}

def _to_camel(obj: dict) -> dict:
    return camelize_dict(obj)


def fetch_all_paginated(url):
    results = []
    while url:
        response = safe_request("GET", url)
        results.extend(response.json())
        
        link_header = response.headers.get("Link")
        next_url = None
        if link_header:
            links = link_header.split(",")
            for link in links:
                parts = link.split(";")
                if len(parts) == 2 and 'rel="next"' in parts[1]:
                    next_url = parts[0].strip()[1:-1]  # Remove the <> at the beginning and end
                    break
        url = next_url
    return results

def list_advertisers():
    url = f"{BASE_URL}/organizations/{ORGANIZATION_ID}/advertisers?per_page=100"
    return fetch_all_paginated(url)
    
def list_campaigns():
    url = f"{BASE_URL}/organizations/{ORGANIZATION_ID}/campaigns?per_page=100"
    return fetch_all_paginated(url)

def create_campaign_from_model(campaign: CampaignCreate) -> dict:
    return create_campaign(_to_camel(campaign.model_dump(exclude_none=True)))

def create_campaign(payload: dict):
    if not payload.get("title") or not payload.get("advertiserId"):
        raise ValueError("Missing required fields: 'title' and 'advertiserId'")

    url = f"{BASE_URL}/organizations/{ORGANIZATION_ID}/campaigns"
    response = safe_request("POST", url, json=payload)
    return response.json()

def get_campaign(campaign_id: str):
    url = f"{BASE_URL}/organizations/{ORGANIZATION_ID}/campaigns/{campaign_id}"
    response = safe_request("GET", url)
    return response.json()

def update_campaign_from_model(campaign_id: str, update: CampaignUpdate) -> dict:
    return update_campaign(campaign_id, _to_camel(update.model_dump(exclude_none=True)))

def update_campaign(campaign_id: str, payload: dict):
    url = f"{BASE_URL}/organizations/{ORGANIZATION_ID}/campaigns/{campaign_id}"
    response = safe_request("PUT", url, json=payload)
    return response.json()
