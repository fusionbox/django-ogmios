import os

from setuptools import setup

version = '0.9.0'


def read_file(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fp:
        return fp.read()


setup(name='django-ogmios',
      version=version,
      author="Fusionbox, Inc.",
      author_email="programmers@fusionbox.com",
      url="https://github.com/fusionbox/django-ogmios",
      keywords="email send easy simple helpers django",
      description="Just sends email. Simple, easy, multiformat.",
      long_description=read_file('README.rst') + '\n\n' + read_file('CHANGELOG.rst'),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Communications :: Email',
          'Topic :: Software Development :: Libraries'
      ],
      install_requires=[
          'Django>=1.7,<1.9'
          'PyYAML',
          'Markdown',
          'html2text',
      ],
      packages=['ogmios'],
      )
