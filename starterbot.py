import os
import time
import re
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM



def get_new_messages(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            message = event["text"]
            return message, event["channel"]
    return None, None


def check_sexist(message, channel):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """

    sexist_list=[ "men will be men", "girls are like that"]

    if message in sexist_list:
        return True
    
    return False

def handle_command(channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    
    response = "Caution, Testosterone Levels have now reached 125%!"
    
        # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response
        )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            message, channel = get_new_messages(slack_client.rtm_read())

            if message:
                check_sexist_message=check_sexist(message, channel)

                if check_sexist_message== True:
                    handle_command(channel)

            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")

