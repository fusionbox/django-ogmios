from __future__ import absolute_import

import collections
import os

import yaml
import markdown
import html2text
import six

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import Template, Context, TemplateDoesNotExist
from django.utils.functional import cached_property

from .loaders import get_template_source

VALID_KEYS = set(['to', 'cc', 'bcc', 'subject', 'attachments',
                  'from', 'headers', 'content-type'])
REQUIRED_KEYS = set(['to', 'subject', 'content-type'])

TYPE_PLAIN = 'plain'
TYPE_MARKDOWN = 'markdown'
TYPE_HTML = 'html'

VALID_CONTENT_TYPE = set([TYPE_PLAIN, TYPE_MARKDOWN, TYPE_HTML])


class TemplateYAMLLoader(yaml.SafeLoader):
    """
    Dirty hack to ignore curly braces when parsing yaml
    """

    def fetch_flow_mapping_start(self):
        """
        { has been encountered
        """
        return self.fetch_plain()

    def fetch_flow_mapping_end(self):
        """
        } has been encountered
        """
        return self.fetch_plain()


class OgmiosError(Exception):
    pass


class EmailTemplateError(OgmiosError):
    pass


class EmailSender(object):

    def __init__(self, filename, context, template_loader=None, attachments=None):
        self.filename = filename
        self.context = context
        self.template_loader = template_loader
        self.attachments = attachments or []

    def get_from(self):
        from_addr = self.data.get('from', settings.DEFAULT_FROM_EMAIL)
        return self.render_string(from_addr)

    def render_string(self, string):
        return Template(string).render(Context(self.context))

    def get_template_source(self):
        return loaders.get_template_source(self)

    @cached_property
    def content(self):
        source = self.get_template_source()

        if source is None:
            raise TemplateDoesNotExist(self.filename)

        return source.split('\n---\n')

    @cached_property
    def data(self):
        data = yaml.load(self.content[0], Loader=TemplateYAMLLoader)

        if not (set(data.keys()) <= VALID_KEYS):
            invalid_keys = set(data.keys()) - VALID_KEYS
            raise EmailTemplateError("Unknown keys: {}".format(', '.join(invalid_keys)))
        if not (set(data.keys()) >= REQUIRED_KEYS):
            missing_keys = REQUIRED_KEYS - set(data.keys())
            raise EmailTemplateError("Missing keys: {}".format(', '.join(missing_keys)))
        if data['content-type'] not in VALID_CONTENT_TYPE:
            raise EmailTemplateError("Unknown content type: {}".format(data['content-type']))
        return data

    def get_recipients(self, name):
        """
        For example get_recipients('to')
        """
        return [
            dest.strip()
            for dest in self.render_string(self.data[name]).split(',')
            if dest.strip()  # Ignore multiple comas like: "email1, , email2"
        ]

    def get_subject(self):
        return self.render_string(self.data['subject'])

    def validate_attachments(self):
        for attachment in self.attachments:
            if isinstance(attachment, six.string_types):
                # Allow specifying an attachment with just
                # a path to the filename
                continue
            else:
                key_set = set(attachment.keys())
                if len(key_set & set(['path', 'data'])) != 1:
                    # Path or data are mutually exclusive.
                    raise OgmiosError("You must specify either a path to an attachment "
                                      "or give a file-like object with the data.")
                if not 'name' in key_set:
                    raise OgmiosError("You must specify the filename to send the attachment as.")


    def handle_attachments(self, email):
        for attachment in self.attachments:
            if isinstance(attachment, six.string_types):
                email.attach_file(attachment)
            else:
                # name is required
                name = attachment['name']
                # type may not be explicitly specified
                mimetype = attachment.get('type')

                if 'data' in attachment:
                    data = attachment['data'].read()
                else:
                    fpath = attachment['path']
                    full_path = os.path.join(fpath)
                    with open(full_path, 'r') as file_:
                        data = file_.read()

                if mimetype:
                    email.attach(name, data, mimetype)
                else:
                    email.attach(name, data)


    def get_headers(self):
        for key, value in self.data['headers'].items():
            yield key, self.render_string(value)

    @cached_property
    def body(self):
        if self.data['content-type'] == TYPE_PLAIN:
            return self.render_string(self.content[1])
        else:
            # Even if this is Markdown, we render the markdown, and convert it to text.
            # Because markdown -> html -> html2text is cleaner plain text than plain markdown.
            return html2text.html2text(self.html)

    @cached_property
    def html(self):
        if self.data['content-type'] == TYPE_PLAIN:
            return None
        elif self.data['content-type'] == TYPE_MARKDOWN:
            return markdown.markdown(self.render_string(self.content[1]))
        elif self.data['content-type'] == TYPE_HTML:
            return self.render_string(self.content[1])

    def send(self):
        to = self.get_recipients('to')
        if len(to) == 0:
            raise EmailTemplateError("You gotta give some recipients.")

        self.validate_attachments()

        kwargs = dict(
            subject=self.get_subject(),
            to=to,
            from_email=self.get_from(),
            body=self.body,
        )
        if 'cc' in self.data:
            kwargs.update(cc=self.get_recipients('cc'))
        if 'bbc' in self.data:
            kwargs.update(bcc=self.get_recipients('bcc'))
        if 'headers' in self.data:
            kwargs.update(headers=dict(self.get_headers()))

        if self.html is None:
            email = EmailMessage(**kwargs)
        else:
            email = EmailMultiAlternatives(**kwargs)
            email.attach_alternative(self.html, 'text/html')

        self.handle_attachments(email)

        email.send()


def send_email(template, context, sender_class=EmailSender, attachments=None):
    return sender_class(template, context, attachments=attachments).send()
