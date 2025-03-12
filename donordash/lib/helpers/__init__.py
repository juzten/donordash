# -*- coding: utf-8 -*-

from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from donordash import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    with current_app.app_context():

        logging_on = current_app.config.LOGGING_ON
        print_log = current_app.config.PRINTLOG
        if not current_app.config.NOTIFICATIONS_ON:
            return
        #    if kwargs.get('sender'):
        #        sender = kwargs.get('sender')
        #    else:
        sender = current_app.config.MAIL_SENDER

        try:
            msg = Message(
                config.MAIL_SUBJECT_PREFIX + " " + subject,
                sender=sender,
                recipients=to,
                bcc=[current_app.config.CATCH_ALL_EMAIL_ADDRESS],
            )
            #        if kwargs.get('reply_to'):
            #            msg.reply_to = kwargs.get('reply_to')
            msg.reply_to = current_app.config.MAIL_SENDER
            msg.to = to
            msg.body = render_template(template + ".txt", **kwargs)
            msg.html = render_template(template + ".html", **kwargs)
            thr = Thread(target=send_async_email, args=[current_app, msg])
            thr.start()
            # mail.send(msg)
        except Exception as e:
            logit(e)
            logit("Email Error")


def logit(data):
    """Writes data to a text file for logging purposes."""
    with current_app.app_context():
        logging_on = current_app.config.LOGGING_ON
        print_log = current_app.config.PRINTLOG
        if logging_on:
            try:
                with open("log.txt", "a") as f:
                    f.write(data)
                    f.write("\n")
            except Exception:
                pass
            if print_log:
                print(data)
        else:
            print(data)
