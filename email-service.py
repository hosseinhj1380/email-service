import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from imap_tools import MailBox
from email import message_from_string


class Mail:
    def __init__(self, email, password) -> None:
        self.email = email
        self.password = password

    def SendMail(self, subject, body, recipient_list):
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = ", ".join(recipient_list)
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()
            # server.ehlo()
            server.login(self.email, self.password)

            # Send the email
            server.sendmail(self.email, recipient_list, msg.as_string())
            return True, "message sent successfully "

        except Exception as e:
            print(str(e))

        finally:
            server.quit()

    def get_inbox_mails(self, input_search_type):
        try:
            mail = imaplib.IMAP4_SSL(settings.EMAIL_HOST)

            mail.login(
                self.email,
                self.password,
            )
            mail.select("inbox")

            status, data = mail.search(None, input_search_type)

            email_ids = data[0].split()
            result = []

            for i, email_id in enumerate(email_ids):
                status, text = mail.fetch(email_id, "(BODY.PEEK[TEXT])")

                status, header = mail.fetch(email_id, "(BODY.PEEK[HEADER])")

                text, header = self.bytecode2str(text, header)

                msg = message_from_string(header)
                From = msg.get("From")
                result.append(
                    {
                        # "header": header,
                        "id": i + 1,
                        "message_id": msg.get("Message-ID"),
                        "subject": msg.get("Subject"),
                        "text": text,
                        "details": {
                            "Subject": msg.get("Subject"),
                            "From": From,
                            "To": msg.get("To"),
                            "Date": msg.get("Date"),
                            "username": From.split("@")[0],
                        },
                    }
                )
            return True, result
        except Exception as e:
            print(e)
            return False, "error while fetching emails"
        finally:
            mail.logout()

    def get_outbox_mails(self, input_search_type, mail_selection):
        try:
            mail = imaplib.IMAP4_SSL(settings.EMAIL_HOST)

            mail.login(
                self.email,
                self.password,
            )
            mail.select(mail_selection)

            status, data = mail.search(None, input_search_type)

            email_ids = data[0].split()
            result = []

            for i, email_id in enumerate(email_ids):
                status, text = mail.fetch(email_id, "(BODY.PEEK[TEXT])")

                status, header = mail.fetch(email_id, "(BODY.PEEK[HEADER])")

                text, header = self.bytecode2str(text, header)
                msg = message_from_string(header)
                From = msg.get("From")
                result.append(
                    {
                        # "header": header,
                        "id": i + 1,
                        "message_id": msg.get("Message-ID"),
                        "subject": msg.get("Subject"),
                        "text": text,
                        "details": {
                            "Subject": msg.get("Subject"),
                            "From": From,
                            "To": msg.get("To"),
                            "Date": msg.get("Date"),
                            "username": From.split("@")[0],
                        },
                    }
                )

            return True, result

        except Exception as e:
            print(e)
            return False, "error while fetching emails"
        finally:
            mail.logout()

    def save_as_draft_mail(self, subject, body, recipient_email):
        msg = MIMEMultipart()

        msg["From"] = settings.EMAIL_HOST_USER
        msg["To"] = ", ".join(recipient_email)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        try:
            imap_server = imaplib.IMAP4_SSL(settings.EMAIL_HOST)
            imap_server.login(self.email, self.password)

            imap_server.append("Drafts", None, None, msg.as_bytes())

            return True, "message saved as draft"

        except Exception as e:

            print(str(e))

            return False, "internal error while save email as draft "

        finally:
            imap_server.logout()

    def move_mail_to_another_box(self, email_uid, source, dest):
        try:
            with MailBox(settings.EMAIL_HOST).login(
                self.email, self.password, source
            ) as mailbox:
                copy_result, delete_result = mailbox.move(mailbox.uids(email_uid), dest)
            return True, "successfully moved "

        except Exception as e:
            print(e)

            return False, "check value and try again  "

        # finally:
        #     mailbox.logout()

    def copy_mail_to_another_box(self, email_uid, source, dest):
        try:
            with MailBox(settings.EMAIL_HOST).login(
                self.email, self.password, source
            ) as mailbox:
                copy_result, delete_result = mailbox.copy(mailbox.uids(email_uid), dest)

                print(copy_result, delete_result)
            return True, "successfully copied "
        except Exception as e:
            print(
                e,
            )
            return False, "check value and try again "

        # it doesnt need at all
        # finally :
        #     mailbox.logout()

    def reply_and_forward_email(
        self, receiver_email, message_id, subject, body, operation
    ):
        message = MIMEMultipart()
        message["From"] = self.email
        message["To"] = ", ".join(receiver_email)
        message["Subject"] = subject
        message["In-Reply-To"] = message_id
        if operation == "forward":
            message["References"] = message_id
        body = body
        message.attach(MIMEText(body, "plain"))

        smtp_server = settings.EMAIL_HOST
        smtp_port = settings.EMAIL_PORT

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)

            server.starttls()

            # Send the email
            server.login(self.email, self.password)

            server.sendmail(self.email, receiver_email, message.as_string())

            server.quit()
            return True, f"{operation} successed "

        except Exception as e:

            print(f"Failed to send email. Error: {e}operations = {operation}")
            return False, f"Failed to send email. Error: {e}operations = {operation}"

    def mark_mail(self, mail_box, email_uid, mark, boolean):

        try:
            server = imaplib.IMAP4_SSL(settings.EMAIL_HOST)
            server.login(self.email, self.password)
            server.select(mail_box)
            if boolean:
                server.store(str(email_uid), "+FLAGS", f"\\{mark}")
            else:

                server.store(str(email_uid), "-FLAGS", f"\\{mark}")

            server.close()
            server.logout()
            return True, "email marked successfully "
        except Exception as e:

            print(e)
            return False, "error while mark email "

    def bytecode2str(self, text, header):
        return (
            text[0][1].decode("utf-8"),
            header[0][1].decode("utf-8"),
        )
import imaplib
from queue import Queue
from threading import Lock

class IMAPConnectionPool:
    def __init__(self, email , password, pool_size=50):
        self.host = "192.168.20.90"
        # self.port = port
        self.username = email
        self.password = password
        self.pool_size = pool_size
        self._lock = Lock()
        self._connections = Queue(maxsize=pool_size)
        self._create_connections()

    def bytecode2str(self, text, header):
        return (
            text[0][1].decode("utf-8"),
            header[0][1].decode("utf-8"),
        )

    def _create_connections(self):
        for _ in range(self.pool_size):
            connection = imaplib.IMAP4_SSL(self.host)
            connection.login(self.username, self.password)
            self._connections.put(connection)

    def get_connection(self):
        with self._lock:
            if not self._connections.empty():
                return self._connections.get()
            else:
                raise Exception("Connection pool exhausted")

    def release_connection(self, connection):
        with self._lock:
            self._connections.put(connection)


    def get_mail(self,input_search_type):
        mail = self.get_connection()
        
        mail.select("inbox")
        try:
            status, data = mail.search(None, input_search_type)

            email_ids = data[0].split()
            result = []

            for i, email_id in enumerate(email_ids):
                status, text = mail.fetch(email_id, "(BODY.PEEK[TEXT])")

                status, header = mail.fetch(email_id, "(BODY.PEEK[HEADER])")

                text, header = self.bytecode2str(text, header)

                msg = message_from_string(header)
                From = msg.get("From")
                result.append(
                    {
                        # "header": header,
                        "id": i + 1,
                        "message_id": msg.get("Message-ID"),
                        "subject": msg.get("Subject"),
                        "text": text,
                        "details": {
                            "Subject": msg.get("Subject"),
                            "From": From,
                            "To": msg.get("To"),
                            "Date": msg.get("Date"),
                            "username": From.split("@")[0],
                        },
                    }
                )
            return result
        except Exception as e:
            print(e)
            return False, "error while fetching emails"
        finally:
            self.release_connection(mail)
