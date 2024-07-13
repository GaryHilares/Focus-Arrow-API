from abc import ABC, abstractmethod
import smtplib
from email.mime import multipart, text


class AbstractEmailClient(ABC):
    @abstractmethod
    def send(to_address: str, subject: str, message: str):
        raise NotImplementedError


class GmailClient(EmailClient):
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

    def send_email(self, to_address: str, subject: str, content: str):
        msg = multipart.MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.username
        msg["To"] = to_address
        msg.attach(text.MIMEText(content, "html"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(self.username, self.password)
        server.sendmail(self.username, to_address, msg.as_string())
        server.quit()
