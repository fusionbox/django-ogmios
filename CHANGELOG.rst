Changelog
=========

0.12.0 (2025-01-29)
-------------------

- Use old non-strict behavior of getaddresses. Requires latest patch version of Python >= 3.8

0.11.2 (2020-07-02)
-------------------

- Make bcc work


0.11.1 (2018-10-12)
-------------------

- Fix email parsing [#15]


0.11.0 (2018-09-04)
-------------------

- Add support for Django > 1.11 and remove support for all prior versions.


0.10.0 (2016-04-13)
-------------------

- Add support for Django 1.9
- Drop support for Django 1.7
- Move method of adding attachments out of the template
  and require attachments to be passed as an argument to ``send_email()``.


0.9.3 (2015-08-27)
------------------

- Add Django 1.7 compatibility.


0.9.2 (2015-07-16)
------------------

- Fix ``setup.py`` dependencies.
- Fix tests.
- Fix compatibility with django's cached loader.
- Fix context processing.


0.9.1 (2015-06-22)
------------------

- Fix 'From' field always being default


0.9.0 (2015-06-18)
------------------

- Initial version
