import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-storybase-management',
    version = '0.1',
    packages = ['storybase_management'],
    include_package_data = True,
    license = 'MIT License',
    description = 'A simple Django app containing management commands to administer and develop a Storybase instance',
    long_description = README,
    url = 'https://github.com/pitonfoundation/django-storybase-management/',
    author = 'Geoffrey Hing',
    author_email = 'geoffhing@gmail.com',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires = [
        'django',
        'name_generator',
    ],
)
