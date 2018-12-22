import os
import time
import re
import json
import atexit
import time
from slackclient import SlackClient


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# data saving support
SAVE_FILE=os.environ.get('SLACK_SAVE_FILE')
our_data={}

user_list=None

time_parse = re.compile("([0-9]+):([0-9]+)")

#
# Functions
#
def bot_return_help(channel, user, args):
    help = "CWBot: track times for games played at https://www.nytimes.com/crosswords/game/mini\n\n"
    for command in bot_commands:
        if 'help' in bot_commands[command]:
            help += "%-10.10s %s\n" % (command, bot_commands[command]['help'])
    return help

def bot_echo_test(channel, user, args):
    return " ".join(args)

def bot_whoami(channel, user, args):
    user_info = find_user(user)
    # for info in user_info:
    #     print("%-20s: %s" % (info, user_info[info]))

    return_string = ""

    return_string += "userid:    " + user + "\n"
    return_string += "full name: " + user_info['real_name'] + "\n"
    return_string += "name:      " + user_info['name'] + "\n"
    return return_string

def bot_parse_hour_minute(mmss):
    result = time_parse.match(mmss)
    if result:
        return int(result.group(1)) * 60 + int(result.group(2))

    return None

def make_datestr():
    now = time.localtime()
    date = "%04s/%02s/%02s" % (now.tm_year, now.tm_mon, now.tm_mday)
    return date

def bot_add_time(channel, user, args):
    user_info = find_user(user)
    if not user_info:
        return "Unable to find your user information"

    global our_data

    if 'cwtimes' not in our_data:
        our_data['cwtimes'] = {}

    if user not in our_data['cwtimes']:
        our_data['cwtimes'][user] = {
            'times': []
        }

    date = make_datestr()

    time = bot_parse_hour_minute(args[0])
    if not time:
        return "invalid time; must be MM:SS formatted."
    
    our_data['cwtimes'][user]['times'].append({'date': date, 'time': time})

    save_data()

    return "Added a time for you of " + str(time) + " seconds"

def average_score(entries):
    total = 0
    if(len(entries) == 0):
        return 0
    for e in entries:
        total = total + e['time']
    return float(total)/float(len(entries))

def sec_to_hhmm(secs):
    return "%02d:%02d" % (secs/60, secs % 60)

def bot_score(channel, user, args):
    if 'cwtimes' not in our_data:
        return "No scores recorded so far"

    # create a header
    result_msg = "%-30.30s %3s    %s\n" % ("Name", "Cnt", "Average")

    # add each user scores summary
    for user in our_data['cwtimes']:
        user_info = find_user(user)
        ave_score = sec_to_hhmm(average_score(our_data['cwtimes'][user]['times']))
        result_msg += "%-30.30s %3d    %s\n" % (user_info['real_name'], len(our_data['cwtimes'][user]['times']),
                                              sec_to_hhmm(average_score(our_data['cwtimes'][user]['times'])))
    return result_msg

def bot_entries(channel, user, args):
    result_str = ""
    for entry in our_data['cwtimes'][user]['times']:
        result_str += "%-15.15s %s\n" % (entry['date'], sec_to_hhmm(entry['time']))
    return result_str

bot_commands = {
    'help':   {'fn': bot_return_help,
               'help': "Get help (this message)"},
    'echo':   {'fn': bot_echo_test,
               'help': "Repeat back whatever I say"},
    'whoami': {'fn': bot_whoami,
               'help': "print out information about me"},
    'time':   {'fn': bot_add_time,
               'help': "Add todays' time to your running score"},
    'scores': {'fn': bot_score,
               'help': "Display the scores to date"},
    'score':   {'fn': bot_score},
    'entries': {'fn': bot_entries,
                'help': "List each recorded entry (for you)"}
}

#
# Support
#
def find_user(id):
    for user in user_list:
        if user['id'] == id:
            return user
    return None

#
# Load and Save Data
#
def save_data():
    with open(SAVE_FILE, "w") as outf:
        outf.write(json.dumps(our_data, sort_keys=True, indent=4))
        outf.write("\n")
        print("saved data")

def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as inf:
            global our_data
            print("loading data...")
            our_data=json.loads(inf.read())

#
# Connection / routing
#
def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"], event["user"]
    return None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel, user):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None

    # This is where you start to implement more commands!
    parts = command.split()
    if parts[0] in bot_commands:
        fn = bot_commands[parts[0]]['fn']
        response = fn(channel, user, parts[1:]) # call it
    else:
        response = "Sorry, I don't that command.  Try 'help'?"

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    load_data()
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        user_list = slack_client.api_call("users.list")['members']
        
        while True:
            command, channel, user = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel, user)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")

