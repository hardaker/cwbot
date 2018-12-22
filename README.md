# Crossword Time Tracking Bot

The CW slack bot is designed to track daily(ish) scores for multiple
people.

# Running it:

Once you have a [slack API
token](https://api.slack.com/apps/AEZHZ71A4/install-on-team?success=1),
fill out the two two variables in this short bash script:

```
export SLACK_BOT_TOKEN=xoxb-481632186182-510179647172-1DQUiP22QfFWBpDYoee3mcbH
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

# TODO

- allow recording a time for a past date

