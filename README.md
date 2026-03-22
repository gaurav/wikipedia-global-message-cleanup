# Wikipedia Global Message Cleanup

Python scripts to clean up Wikipedia GlobalMessage delivery lists.

All the scripts need [uv](https://docs.astral.sh/uv/) to run them.

## check-last-contribution — Check the last contribution times for a list of Wikipedia users

This is intended to be used to clean up a list of Wikipedia usernames, such as from a GlobalMessage
delivery list.

The idea is that you can download the MediaWiki source code from a GlobalMessage list, such as the
[North Carolina Wikipedians list](https://meta.wikimedia.org/wiki/Global_message_delivery/Targets/North_Carolina_Wikipedians)
to a file called e.g. `global-message-list-2025sep15.mediawiki.txt`.

```shell
$ uv run check-last-contribution global-message-list-2025sep15.mediawiki.txt -o list-with-last-edited-dates.tsv
```

You can also specify additional sites that should be checked for each user by
using `-s commons.wikimedia.org -s wikidata.org`. No username/site combination will be checked
more than once. Subsequent mentions produce a row with `username` and `site` populated but `last_edit_utc` and `last_edit_date` left empty, and `threshold_result` set to `duplicate`.

You can also specify two thresholds:
* The `--inactive-from` year is the minimum year a user must have edited to avoid being marked as delete (e.g. `2015`).
* The `--active-from` year is the minimum year a user must have edited to be marked as active (e.g. `2020`).

At this moment, each line in the input file is retained in the output file in order to support moving
names around in section -- we'll probably change this behavior in the future so that we produce
a TSV file with the last edit information, followed by several MediaWiki files that can be inserted
into the active and inactive pages. The whole workflow of this script needs an overhaul, really.

Some example output (with lines excised for privacy):

| **line_no** | **line** | **username** | **site** | **last_edit_utc** | **last_edit_date** | **threshold_result** |
|-------------|----------|--------------|----------|-------------------|--------------------|----------------------|
| 1 | See also: the list of [[/Events\|event attendees]] … | | | | | |
| 2 | | | | | | |
| 3 | \== Users from our ''[[North Carolina Wikipedians#Participants and Supporters\|Participants and Supporters list]]'' == | | | | | |
| 26 | \* {{target \| user = Gaurav \| site = en.wikipedia.org}} | Gaurav | wikidata.org | 2025-09-11T04:32:39Z | 2025-09-11 | active |
| 26 | \* {{target \| user = Gaurav \| site = en.wikipedia.org}} | Gaurav | en.wikipedia.org | 2025-09-19T05:10:24Z | 2025-09-19 | active |
| 26 | \* {{target \| user = Gaurav \| site = en.wikipedia.org}} | Gaurav | commons.wikimedia.org | 2025-09-19T03:59:10Z | 2025-09-19 | active |
| 152 | \* {{target \| user = Gaurav \| site = en.wikipedia.org}} | Gaurav | en.wikipedia.org | | | duplicate |
| 475 | \* {{target \| user = Gaurav \| site = en.wikipedia.org}} | Gaurav | en.wikipedia.org | | | duplicate |
| 555 | \* {{target \| user = Gaurav \| site = en.wikipedia.org}} | Gaurav | en.wikipedia.org | | | duplicate |
| 598 | \* {{target \| user = Gaurav \| site = en.wikipedia.org}} | Gaurav | en.wikipedia.org | | | duplicate |

### Testing

This package has some unit tests. To run them, run `uv run pytest`.
