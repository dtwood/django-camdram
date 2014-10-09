from django.core.management.base import BaseCommand, CommandError
from issues import models
import email
import re
from django.conf import settings
from email_reply_parser import EmailReplyParser
from django.utils import timezone


class Command(BaseCommand):
    args = '<file file file ...>'
    help = 'Parse the email files and add them to the issue tracker'

    def handle(self, *args, **options):
        for filename in args:
            with open(filename, 'r') as f:
                mail = email.message_from_file(f)
                _ , to_addr = iemail.utils.parseaddr(mail.get('To'))
                local_part = re.match(r'([^@]*)@' + settings.EMAIL_FROM_DOMAIN,to_addr)
                if local_part:
                    local_part = local_part.group(1)
                    message = []
                    for part in mail.walk():
                        if part.get_content_type() == 'text/plain':
                            message.append(part.get_payload())
                    body = EmailReplyParser.parse_reply('\n'.join(message))
                    match = re.match(r'issue-([0-9]*)', local_part)
                    _ , from_addr = email.utils.parse(mail.get('From'))
                    if local_part in settings.NEW_ISSUE_ADDRESSES:
                        subject = mail.get('Subject')
                        issue = models.Issue(name=subject, desc=body, email=from_addr, opened=timezone.now())
                        issue.save()
                    elif match:
                        key = match.group(1)
                        issue = models.Issue.objects.get(pk=key)
                        issue.add_message(from_addr, body)
