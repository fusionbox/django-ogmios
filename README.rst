=============
Django-Ogmios
=============
.. image:: https://travis-ci.org/fusionbox/django-ogmios.svg?branch=master
    :target: https://travis-ci.org/fusionbox/django-ogmios
    :alt: Build Status

Just sends emails. Simple, easy, multiformat.

For those wondering, `Ogmios <https://en.wikipedia.org/wiki/Ogmios>`_ is just the Gallic god of eloquence.

Quickstart
==========

Install from PyPI with ``pip``: ``pip install django-ogmios``.

``yourproject/templates/mail/template.html``::

    from: admin@example.org
    to: Jane Doe <jane.doe@example.net>, {% for u in users %}{{ user.email }}, {% endfor %}
    cc: John Doe <john.doe@example.org>, {{ copy_user.get_full_name }} <{{ copy_user.email }}>
    bcc: anonymous@example.org, secret@example.com
    subject: The whole email is a template
    content-type: markdown
    headers:
      Reply-To: Jaqueline <jaqueline@example.net>
      Organization: Example.org, Inc.
    ---
    {% load special_filter %}

    This is a list of special items:

    {% for item in item_list %}
       * {{ item|special }}
    {% endfor %}


.. code:: python

    import ogmios

    ogmios.send_email('mail/template.html',
                      {'item_list': ['Hello']},
                      attachments=[{
                           'path': '/path/to/file/',
                           'name': 'file.txt',
                           'type': 'text/plain',
                       }])


This will render the content as markdown, and send the email with an HTML part and a Plaintext part.
For attachments, it is possible to just specify the path, or the path, filename and mimetype.

Tips
====

Resend an email with different context:

.. code:: python

    import functools
    import ogmios

    from myapp.models import User

    send_registration = functools.partial(ogmios.send, 'mail/template.html')
    send_registration({'user': User.objects.get(pk=1337)})
