import time
import logging
import requests

class WikimediaAPIClient:
    """Handles API requests to Wikimedia sites with retry logic."""

    def __init__(self, user_agent: str, max_retries: int = 5, backoff_factor: int = 2):
        self.user_agent = user_agent
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def get_last_edit(self, username: str, site: str) -> str:
        """Get the last edit timestamp for a username from the given site using MediaWiki API with retries."""
        api_url = f"https://{site}/w/api.php"
        params = {
            "action": "query",
            "list": "usercontribs",
            "ucuser": username,
            "uclimit": 1,
            "ucprop": "timestamp",
            "format": "json",
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.get(
                    api_url,
                    params=params,
                    timeout=10,
                    headers={"User-Agent": self.user_agent},
                )
                resp.raise_for_status()
                data = resp.json()
                contribs = data.get("query", {}).get("usercontribs", [])
                return contribs[0]["timestamp"] if contribs else ""
            except Exception as e:
                if attempt == self.max_retries:
                    logging.error(f"Failed to get data for {username}@{site}: {e}")
                    return ""
                sleep_time = self.backoff_factor ** (attempt - 1)
                logging.info(
                    f"Request failed for {username}@{site}, retrying in {sleep_time}s..."
                )
                time.sleep(sleep_time)
        return ""
