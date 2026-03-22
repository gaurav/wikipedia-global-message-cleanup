import logging
import re
from typing import Iterator
from .models import UsernameWithSite

# Case-insensitive so {{TARGET ...}} and other variants are caught as malformed.
# The extraction regex below is intentionally case-sensitive (MediaWiki treats
# template names as case-sensitive on the first character), so non-lowercase
# variants would otherwise be silently ignored.
_LOOSE_TARGET_RE = re.compile(r"{{\s*target\b", re.IGNORECASE)


class MediaWikiParser:
    """Parses MediaWiki GlobalMessage delivery list format."""

    def parse_line(self, line: str) -> Iterator[UsernameWithSite]:
        """Extract username and site from lines like {{target | user = Username | site = en.wikipedia.org}}."""
        targets = re.findall(
            r"{{\s*target\s*\|\s*user\s*=\s*(.+?)\s*(?:\|\s*site\s*=\s*(.+?)\s*)?\s*}}",
            line,
        )
        results = []
        for target in targets:
            username = target[0].strip()
            if not username:
                continue
            site = target[1].strip() if target[1] else None
            results.append(UsernameWithSite(username, site))
        if not results and _LOOSE_TARGET_RE.search(line):
            logging.warning(
                "Possible malformed {{target}} template — please double-check: %r", line
            )
        return iter(results)
