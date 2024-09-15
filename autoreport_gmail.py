import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

from dotenv import load_dotenv
load_dotenv()
key = os.getenv('API_KEY')

report_file_path = "./Der_Karabinier.pdf"
sender = "mcontini.throwaway@gmail.com"
temp_token = key # PORCO DIO NON PUBBLICARLO SU GITHUB
                                    # vd gitignore env
recipient = sender

smtp_server = "smtp.gmail.com"
smtp_port = 587
msg = MIMEMultipart()

msg['From'] = sender
msg['To'] = recipient
msg['Subject'] = "Dammi un bacio ti prego ^_^"
body = "Ciao,\n\nIn allegato trovi il report giornaliero.\n\nSaluti."

msg.attach(MIMEText(body, 'plain'))
attachment = open(report_file_path, "rb") # PDF

part = MIMEBase('application', 'octet-stream')
part.set_payload(attachment.read())

encoders.encode_base64(part)

part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(report_file_path)}")
msg.attach(part)

attachment.close()

server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()

server.login(sender, temp_token)

# Conversione del messaggio in stringa e invio
body_to_text = msg.as_string()
server.sendmail(sender, recipient, body_to_text)


server.quit()
