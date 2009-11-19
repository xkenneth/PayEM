import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os

from config import gmail_user, gmail_password

def mail(to, subject, text, attach=None):
   msg = MIMEMultipart()

   msg['From'] = gmail_user
   msg['To'] = to
   msg['Subject'] = subject
   
   msg.attach(MIMEText(text))

   if attach is not None:
      

      part = MIMEBase('application', 'octet-stream')
      part.set_payload(open(attach, 'rb').read())
      Encoders.encode_base64(part)
      part.add_header('Content-Disposition',
                      'attachment; filename="%s"' % os.path.basename(attach))
      msg.attach(part)

   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(gmail_user, gmail_password)
   mailServer.sendmail(gmail_user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

if __name__ == '__main__':
   
   mail(test_email_addr,
        "Test Subject!",
        "Test Message.",
        )
