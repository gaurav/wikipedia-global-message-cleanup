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
$ uv run check-last-contribution.py global-message-list-2025sep15.mediawiki.txt -o list-with-last-edited-dates.tsv
```

You can also specify additional sites that should be checked for each user by
using `-s commons.wikimedia.org -s wikidata.org`. No username/site combination will be checked
more than once, and subsequent mentions of that username will have blank fields in the output TSV.

You can also specify two thresholds:
* The `--threshold-inactive` year will be assumed to be the most recent year after which usernames will be marked as inactive (e.g. `2015`).
* The `--threshold-active` year will be assumed to be the most recent year after which usernames will be marked as active (e.g. `2020`).

At this moment, each line in the input file is retained in the output file in order to support moving
names around in section -- we'll probably change this behavior in the future so that we produce
a TSV file with the last edit information, followed by several MediaWiki files that can be inserted
into the active and inactive pages. The whole workflow of this script needs an overhaul, really.

Some example output (with lines excised for privacy):

| **line_no**                                                                               | **line**                                                                                                                                      | **username** | **site**                                              | **last_edit_utc**    | **last_edit_date** | **threshold_result** |
|-------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------| ------------ | ----------------------------------------------------- | -------------------- | ------------------ | -------------------- |
| 1                                                                                         | See also: the list of [[/Events\|event attendees]] if you want to reach everybody who's ever attended a [[North Carolina Wikipedians]] event. |              |                                                       |                      |                    |                      |
| 2                                                                                         |                                                                                                                                               |              |                                                       |                      |                    |
| 3                                                                                         | \== Users from our ''[[North Carolina Wikipedians#Participants and Supporters\|Participants and Supporters list]]'' ==                        
| 26                                                                                        | \* {{target \| user = Gaurav \| site = [en.wikipedia.org](http://en.wikipedia.org)}}                                                          | Gaurav       | [wikidata.org](http://wikidata.org)                   | 2025-09-11T04:32:39Z | 2025-09-11         | active          
| 26                                                                                        | \* {{target \| user = Gaurav \| site = [en.wikipedia.org](http://en.wikipedia.org)}}                                                          | Gaurav       | [en.wikipedia.org](http://en.wikipedia.org)           | 2025-09-19T05:10:24Z | 2025-09-19         | active               |
| 26          | \* {{target \| user = Gaurav \| site = [en.wikipedia.org](http://en.wikipedia.org)}} | Gaurav       | [commons.wikimedia.org](http://commons.wikimedia.org) | 2025-09-19T03:59:10Z | 2025-09-19         | active               |
| 26                                                                                        | \* {{target \| user = Gaurav \| site = [en.wikipedia.org](http://en.wikipedia.org)}}                                                          
| 152                                                                                       | \* {{target \| user = Gaurav \| site = [en.wikipedia.org](http://en.wikipedia.org)}}                                                          
| 475                                                                                       | \* {{target \| user = Gaurav \| site = [en.wikipedia.org](http://en.wikipedia.org)}}                                                          |              |                                                       |                      |                    |                      |
| 501                                                                                                                                                                                                                                   | \* {{target \| user = Gaurav \| site = [en.wikipedia.org](http://en.wikipedia.org)}}                                                          
| 555                                                                                       | \* {{target \| user = Gaurav \| site = [en.wikipedia.org](http://en.wikipedia.org)}}                                                          |                                                                                                                                               |                                                       |                      |                    |                      |
| 565                                                                                                                                                                                                                                     | \* {{target \| user = Gaurav \| site = [en.wikipedia.org](http://en.wikipedia.org)}}                                                          
| 598 |  \* {{target \| user = Gaurav \| site = [en.wikipedia.org](http://en.wikipedia.org)}}                                                         |                                                                                                                                               |                                                       |                      |                    |                      |
