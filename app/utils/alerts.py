from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from dotenv import load_dotenv
# import requests

load_dotenv()




conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAILGUN_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAILGUN_PASSWORD"),
    MAIL_FROM=os.getenv("MAILGUN_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.mailgun.org",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
) 



async def send_email_alert(to_email, subject, body):
    message = MessageSchema(
        subject=subject,
        recipients=[to_email],
        body=body,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)



# Currently not in use

# def send_simple_message():
#   	return requests.post(
#   		"https://api.mailgun.net/v3/sandbox8299ba1fd7794f909d6be254b32969ea.mailgun.org/messages",
#   		auth=("api", os.getenv('API_KEY', 'API_KEY')),
#   		data={"from": "Mailgun Sandbox <postmaster@sandbox8299ba1fd7794f909d6be254b32969ea.mailgun.org>",
# 			"to": "Winston Li <randston2020@gmail.com>",
#   			"subject": "Hello Winston Li",
#   			"text": "Congratulations Winston Li, you just sent an email with Mailgun! You are truly awesome!"})