import os
from setuptools import setup
from nyanbar import VERSION

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "nyanbar",
    version=VERSION,
    author = "Andrew Gwozdziewycz",
    author_email = "web@apgwoz.com",
    description = ("nyanbar is a progress bar for scripts that uses the Nyan cat instead of other stuff."),
    url='https://github.com/apgwoz/nyanbar',
    license = "LGPL",
    packages=['nyanbar'],
    install_requires=[],
    long_description=read('README'),
    requires=[],
    classifiers=[
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Environment :: Console"
    ]
)
