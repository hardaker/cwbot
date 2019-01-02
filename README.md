# Crossword Time Tracking Bot

The CW slack bot is designed to track daily(ish) scores for multiple
people.

# Running it:

Once you have a [slack API
token](https://api.slack.com/apps/AEZHZ71A4/install-on-team?success=1),
fill out the two two variables in this short bash script:

```
export SLACK_BOT_TOKEN=xoxb-....
export SLACK_SAVE_FILE=/tmp/save.json

python3 cwbot.py
```

# Using It

Within slack you can type @cwbot (or whatever you named yours) with
the following commands:

```
time       Add todays' time to your running score
scores     Display the scores to date
entries    List each recorded entry (for you)

help       Get help (this message)
echo       Repeat back whatever I say
whoami     print out information about me
```

## Example

```
@cwbot time 1:39
Added a time for you of 99 seconds

@cwbot time 1:51
Added a time for you of 111 seconds

...

@cwbot scores
Name                           Cnt    Average
Wes Hardaker                     5    02:53
Someone Else                     1    00:55

```

(clearly, "someone else" is better at crossword puzzles than I am)

# TODO

- allow recording a time for a past date

# Background software

This bot is based off my adaption of the [slack starter bot](https://github.com/hardaker/slack-starterbot).
