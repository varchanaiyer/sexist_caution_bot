import os
import time
import re
from slackclient import SlackClient
from keras.models import load_model
import pickle
import numpy as np
import nltk
from nltk.corpus import stopwords
import os
import re
import sys
import unicodedata
from keras.preprocessing import sequence

pred_list=['Insult', 'Not Insult']

model=load_model('models/model1.h5')
with open('tok.pkl', 'rb') as f:
    tok = pickle.load(f)

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM

def tokenize(sentences):
    
    tokens=[]
    
    for sentence in sentences:
        sentence=nltk.word_tokenize(sentence)
        tokens.append(sentence)
    
    return tokens

def punc(sentences):
    punctuation = dict.fromkeys([i for i in range(sys.maxunicode)
                                 if unicodedata.category(chr(i)).startswith('P')])

    new_sentences=[]
    
    for sentence in sentences:
        sentence = [i.lower() for i in nltk.word_tokenize(sentence.translate(punctuation))]
        sentence= ' '.join(sentence)
        new_sentences.append(sentence)
    
    return new_sentences  

def remove_stopwords(sentences):
    stop_words=set(stopwords.words('english'))
    
    new_sentences=[]
    
    for sentence in sentences:
        sentence = [word for word in sentence.lower().split() if word not in stop_words]
        sentence = ' '.join(sentence)
        new_sentences.append(sentence)
    
    return new_sentences

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

def predict(message):
    comments=[message]
    comments=punc(comments)
    comments=remove_stopwords(comments)
    comments=tokenize(comments)

    sequences = tok.texts_to_sequences(comments)
    max_len=50
    sequences_matrix = sequence.pad_sequences(sequences,maxlen=max_len)
    
    pred=model.predict(sequences_matrix)
    
    if pred_list[np.argmax(pred)] == 'Insult':
        return True
    
    return False


def check_sexist(message, channel):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    message=message.lower()
    sexist_list=[ "men will be men", "girls are like that",
                 'as good as a man', 'like a man', 
                'for a girl', 'smart for a girl', 'love of a woman',
            'men are better', 'girls cant do that']

    if any(ext in message for ext in sexist_list):
        return True
    elif predict(message):
        return True
    
    return False

def handle_command(channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    
    response = "Caution, that was a sexist remark. We do not encourage such remarks in our workspace!"
    
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

