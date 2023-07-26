import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import mimetypes
from email import encoders
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase

def send_email(file_path, subject):
    msg = MIMEMultipart()
    msg['From'] = 'woodenarm@ukr.net'
    msg['To'] = 'your_assistant_backup@aol.com'
    msg['Subject'] = subject
    
    filename = os.path.basename(file_path)
    ftype, encoding = mimetypes.guess_type(file_path)
    file_type, subtype = ftype.split("/")
    
    print(subtype)
    
    if file_type == "text":
         with open(f"{file_path}", "rb") as f:
            file_path = MIMEBase(file_type, subtype)
            file_path.set_payload(f.read())
            encoders.encode_base64(file_path)
    elif file_type == "image":
        with open(f"{file_path}", "rb") as f:
            file_path = MIMEImage(f.read(), subtype)
    elif file_type == "audio":
        with open(f"{file_path}", "rb") as f:
            file_path = MIMEAudio(f.read(), subtype)
    elif file_type == "application":
        with open(f"{file_path}", "rb") as f:
            file_path = MIMEApplication(f.read(), subtype)
    else:
        with open(f"{file_path}", "rb") as f:
            file_path = MIMEBase(file_type, subtype)
            file_path.set_payload(f.read())
            encoders.encode_base64(file_path)
    file_path.add_header('content-disposition', 'attachment', filename=filename)
    msg.attach(file_path)

    server = smtplib.SMTP_SSL('smtp.ukr.net', 465)
    server.ehlo('woodenarm@ukr.net')
    server.login('woodenarm@ukr.net', 'XteYMm8ZFQKdWJ7a')
    server.auth_plain()
    server.send_message(msg)
    server.quit()