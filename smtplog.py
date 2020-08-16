from logging.handlers import SMTPHandler
import smtplib


class MySMTPHandler(SMTPHandler):
    """A class with overridden emit() method for proper emails sending."""
    def emit(self, record):
        with smtplib.SMTP(self.mailhost, self.mailport) as smtpobj:
            smtpobj.ehlo()
            smtpobj.starttls()
            smtpobj.login(self.username, self.password)
            smtpobj.sendmail(from_addr=self.fromaddr, 
                             to_addrs=self.toaddrs, 
                             msg=f'Subject: Responderbot error\n\n{self.format(record)}')
