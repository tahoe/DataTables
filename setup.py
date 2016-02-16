from setuptools import setup
import os

desc = open("readme.rst").read() if os.path.isfile("readme.rst") else ""


setup(
    name='flask_datatables',
    version='0.6.5',
    packages=['flask_datatables', 'flask_datatables.views'],
    url='https://github.com/tahoe/flask_datatables/',
    download_url='https://github.com/tahoe/flask_datatables/tarball/0.6.5',
    license='MIT',
    long_description=desc,
    keywords='sqlalchemy datatables jquery flask-restless flask-restful',
    author='Dennis Durling',
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
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
