from twilio.rest import Client
from twilio_key import *

account_sid = ACCOUNT_SID
auth_token = AUTH_TOKEN


client = Client(account_sid, auth_token)

def format_message(text):

    if type(text) == str:
        return text
    else:
        return str(text)

def create_message(text):

    formatted_text = format_message(text)
    message = client.messages.create(
                                body=formatted_text,
                                from_='+18562915621',
                                to='+16317043733'
                            )

    return message

if __name__ == '__main__':

    create_message('Running')