from email.mime.text import MIMEText
from email.utils import formataddr
from smtplib import SMTP

from app.email_template import html_email

from .config import settings


class Email:
    def __init__(self, usr, pwd, server="smtp.gmail.com", port=587):
        self.user = usr
        self.password = pwd
        self.server = server
        self.port = port

    def send_message(self, content: str, subject: str, mail_to: str):
        message = MIMEText(content, "html", "utf-8")
        message["Subject"] = subject
        message["From"] = formataddr(("diractly", settings.mail_sender))
        message["To"] = mail_to

        mail_server = SMTP(self.server, self.port)
        mail_server.ehlo()
        mail_server.starttls()
        mail_server.ehlo()
        mail_server.login(self.user, self.password)
        mail_server.sendmail(self.user, mail_to, message.as_string())
        mail_server.quit()

    def send_confirmation_message(self, token: str,
                                  mail_to: str,
                                  is_subscriber: bool = True,
                                  subject: str = "Activate your account and get a sample CV chosen by an expert "
                                                 "recruiter"):
        confirmation_url = "{}/verify/{}".format(settings.base_url, token)
        if not is_subscriber:
            confirmation_url = "{}/org/verify/{}".format(settings.base_url, token)

        message = html_email.format(link=confirmation_url)
        self.send_message(message, subject=subject, mail_to=mail_to)

    def send_resource(self, resource: str, subject: str, body: str, mail_to: str):
        # confirmation_url = "{}/verify/{}".format(settings.base_url, token)
        message = """
                    <html>
                      <head></head>
                      <body>
                        {body}
                        {link}
                      </body>
                    </html>""".format(body=body,
                                      link=resource
                                      )
        # row = "<tr><td>" "<a href=" + confirmation_url + ">" + "verify your email" + "</a>" "</td></tr>"
        # message = message.format(link=confirmation_url, text=confirmation_url)
        # message = html_email.format(link=confirmation_url)
        self.send_message(message, subject, mail_to)
