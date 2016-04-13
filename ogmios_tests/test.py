from tempfile import NamedTemporaryFile

from django.core import mail
from django.test import TestCase, override_settings
from six import StringIO

from ogmios import send_email, OgmiosError, EmailSender

CACHED_TEMPLATE_LOADER_SETTINGS = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'loaders': (('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]),)
        },
    }
]


def get_message_text(email):
    return email.message().get_payload()[0].get_payload()


class SendEmailTest(TestCase):

    def test_send_to(self):
        to = 'user@example.com'

        send_email('to.md', {'to': to})

        assert len(mail.outbox) == 1
        assert len(mail.outbox[0].to) == 1
        assert to in mail.outbox[0].to

    def test_send_attachment(self):
        # Encode to bytes for Python 3 compatibility
        content = 'Some content'.encode('utf-8')

        with NamedTemporaryFile() as fp:
            fp.write(content)
            fp.flush()

            send_email('attachment.md',
                       context={},
                       attachments=[fp.name]
            )

        assert len(mail.outbox) == 1
        assert len(mail.outbox[0].attachments) == 1
        assert mail.outbox[0].attachments[0][1] == content

    def test_send_renamed_attachment_without_mimetype(self):
        content = 'Some content'

        with NamedTemporaryFile() as fp:
            # Encode to bytes for Python 3 compatibility.
            fp.write(content.encode('utf-8'))
            fp.flush()

            send_email('attachment.md',
                       context={},
                       attachments=[{
                           'path': fp.name,
                           'name': 'file_test.txt',
                       }])

        assert len(mail.outbox) == 1
        assert len(mail.outbox[0].attachments) == 1
        assert mail.outbox[0].attachments[0][1] == content
        assert mail.outbox[0].attachments[0][0] == 'file_test.txt'

    def test_rename_attachment(self):
        content = 'Some content'

        with NamedTemporaryFile() as fp:
            # Encode to bytes for Python 3 compatibility.
            fp.write(content.encode('utf-8'))
            fp.flush()

            send_email('attachment.md',
                       context={},
                       attachments=[{
                           'path': fp.name,
                           'name': 'file.txt',
                           'type': 'text/plain',
                       }])

        assert len(mail.outbox) == 1
        assert len(mail.outbox[0].attachments) == 1
        assert mail.outbox[0].attachments[0][1] == content
        assert mail.outbox[0].attachments[0][0] == 'file.txt'

    def test_filelike_object_attachment(self):
        content = "This is some data"
        content_file = StringIO(content)

        send_email('attachment.md',
                   context={},
                   attachments=[{
                       'data': content_file,
                       'name': 'data.txt'
                   }])

        assert len(mail.outbox) == 1
        assert len(mail.outbox[0].attachments) == 1
        assert mail.outbox[0].attachments[0][1] == content
        assert mail.outbox[0].attachments[0][0] == 'data.txt'

    def test_attachment_validation(self):
        content = 'Some content'

        with NamedTemporaryFile() as fp:
            fp.write(content.encode('utf-8'))
            fp.flush()
            with self.assertRaises(OgmiosError):
                send_email('attachment.md',
                           context={},
                           attachments=[{
                               'name': 'file.txt'
                           }])

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

    def test_context_application(self):
        context = {
            'to_name': 'Leroy Jenkins',
            'to_address': 'leroooooooooooooooooooooooooy.mmmmm.jenkiiiiiiiiiiins@gmail.com',
            'from_name': 'Onyxia',
            'from_address': 'onyxia@wow.blizzard.net',
            'subject': 'Raid',
            'survival_percent': "33.3 (repeating of course) percent",
        }

        send_email('context.html', context)

        sent_mail = mail.outbox[0]

        assert sent_mail.to[0] == '{} <{}>'.format(context['to_name'], context['to_address'])
        assert sent_mail.from_email == '{} <{}>'.format(context['from_name'], context['from_address'])
        assert sent_mail.subject == context['subject']
        assert get_message_text(sent_mail).strip() == "Chance of survival: {}".format(context['survival_percent'])

    @override_settings(TEMPLATES=CACHED_TEMPLATE_LOADER_SETTINGS)
    def test_cached_loader(self):
        send_email('html.html', {})

        assert len(mail.outbox) == 1
        message = mail.outbox[0].message()
        assert message.is_multipart()
        content_types = {m.get_content_type() for m in message.get_payload()}
        assert content_types == {'text/plain', 'text/html'}


class EmailSenderTest(TestCase):
    def test_build_message(self):
        to = 'user@example.com'
        message = EmailSender('to.md', {'to': to}).build_message()
        assert message.to == [to]
