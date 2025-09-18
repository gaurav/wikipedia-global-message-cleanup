# Wikipedia Global Message Cleanup

Python scripts to clean up Wikipedia GlobalMessage delivery lists.

All the scripts need [uv](https://docs.astral.sh/uv/) to run them.

## check-last-contribution.py - Check the last contribution times for a list of Wikipedia users

This is intended to be used to clean up a list of Wikipedia usernames, such as from a GlobalMessage
delivery list.

The idea is that you can download the MediaWiki source code from a GlobalMessage list, such as the
[North Carolina Wikipedians list](https://meta.wikimedia.org/wiki/Global_message_delivery/Targets/North_Carolina_Wikipedians)
to a file called e.g. `global-message-list-2025sep15.mediawiki.txt`.

```shell
$ uv run check-last-contribution.py global-message-list-2025sep15.mediawiki.txt
```
