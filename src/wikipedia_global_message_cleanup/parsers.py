import re
from typing import Iterator
from .models import UsernameWithSite


class MediaWikiParser:
    """Parses MediaWiki GlobalMessage delivery list format."""

    def parse_line(self, line: str) -> Iterator[UsernameWithSite]:
        """Extract username and site from lines like {{target | user = Username | site = en.wikipedia.org}}."""
        targets = re.findall(
            r"{{\s*target\s*\|\s*user\s*=\s*(.+?)\s*(?:\|\s*site\s*=\s*(.+?)\s*)?\s*}}",
            line,
        )
        for target in targets:
            username = target[0].strip()
            site = target[1] if target[1] else None
            yield UsernameWithSite(username, site)
