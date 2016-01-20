from setuptools import setup
import os

desc = open("readme.rst").read() if os.path.isfile("readme.rst") else ""


setup(
    name='datatables',
    version='0.5.0',
    packages=['datatables'],
    url='https://github.com/tahoe/datatables/',
    license='MIT',
    long_description=desc,
    keywords='sqlalchemy datatables jquery flask flask-restless flask-restful',
    author='Dennis',
    author_email='djdtahoe@gmail.com',
    description='Integrates SQLAlchemy with DataTables (framework Flask)',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'querystring_parser',
        'sqlalchemy',
        'flask',
        'flask-restful'
    ],
)
