from distutils.core import setup

version = __import__('django_medusa').get_version()

setup(name='django-medusa',
    version=version,
    description='A Django static website generator.',
    author='Mike Tigas', # update this as needed
    author_email='mike@tig.as', # update this as needed
    url='https://github.com/mtigas/django-medusa/',
    download_url='https://github.com/mtigas/django-medusa/downloads',
    packages=['django_medusa'],
    install_requires=['django'],
    license='MIT',
    keywords='django static staticwebsite staticgenerator publishing',
    classifiers=["Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
