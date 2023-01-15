import smtplib
from email.mime import multipart, text

class Gmail:
    def send_email(username, password, to_address, subject, content):
        msg = multipart.MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = username
        msg["To"] = to_address
        msg.attach(text.MIMEText(content, "html"))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(username, to_address, msg.as_string())
        server.quit()