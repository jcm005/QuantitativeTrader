from twilio.rest import Client

account_sid = 'ACdc49ab2337c0f134c609be653d8cbfed'
auth_token = 'e745233d00619900a31d5d7abcc9fcf0'

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