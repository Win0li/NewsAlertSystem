from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
import os, requests
from dotenv import load_dotenv
from fastapi import APIRouter
# import requests

router = APIRouter()
load_dotenv()


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str


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
    return 




@router.post("/send_email")
def send_simple_message(request: EmailRequest):
    response = requests.post(
        "https://api.mailgun.net/v3/sandbox8299ba1fd7794f909d6be254b32969ea.mailgun.org/messages",
        auth=("api", os.getenv('MAIL_API_KEY', 'MAIL_API_KEY')), 
        data={
            "from": "Mailgun Sandbox <postmaster@sandbox8299ba1fd7794f909d6be254b32969ea.mailgun.org>",
            "to": request.to,
            "subject": request.subject,
            "text": request.body
        }
    )
    return {
        "status": response.status_code,
        "message": response.text
    }