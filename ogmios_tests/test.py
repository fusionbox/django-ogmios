from tempfile import NamedTemporaryFile

from django.core import mail
from django.test import TestCase

from ogmios import send_email


class SendEmailTest(TestCase):

    def test_send_to(self):
        to = 'user@example.com'

        send_email('to.md', {'to': to})

        assert len(mail.outbox) == 1
        assert len(mail.outbox[0].to) == 1
        assert to in mail.outbox[0].to

    def test_send_attachement(self):
        content = 'Some content'

        with NamedTemporaryFile() as fp:
            fp.write(content)
            fp.flush()

            send_email('attachment.md', {'file': fp.name})

        assert len(mail.outbox) == 1
        assert len(mail.outbox[0].attachments) == 1
        assert mail.outbox[0].attachments[0][1] == content

    def test_rename_attachement(self):
        content = 'Some content'

        with NamedTemporaryFile() as fp:
            fp.write(content)
            fp.flush()

            send_email('renamed_attachment.md', {'file': fp.name})

        assert len(mail.outbox) == 1
        assert len(mail.outbox[0].attachments) == 1
        assert mail.outbox[0].attachments[0][1] == content
        assert mail.outbox[0].attachments[0][0] == 'file.txt'

    def test_markdown(self):
        send_email('markdown.md', {})

        assert len(mail.outbox) == 1
        message = mail.outbox[0].message()
        assert message.is_multipart()
        content_types = {m.get_content_type() for m in message.get_payload()}
        assert content_types == {'text/plain', 'text/html'}

    def test_html(self):
        send_email('html.html', {})

        assert len(mail.outbox) == 1
        message = mail.outbox[0].message()
        assert message.is_multipart()
        content_types = {m.get_content_type() for m in message.get_payload()}
        assert content_types == {'text/plain', 'text/html'}
