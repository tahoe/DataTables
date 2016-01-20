====================
Flask-restful only version of orf/datatables with Flask-restless style filtering
====================
Installation
------------

The package is NOT available on PyPI and is tested on Python 2.7

.. code-block:: bash

    python setup.py install

Usage
-----

NEEDS EDIT

This is SUPER simple. In datatables I provide a function called get_resource that can be used to create a
datatables api endpoint with full flask-restless style filtering built in.

I'll try to pull in some examples from a backbone.js app later.

If you write a function on your SA Base class that returns a list of child table objects then you can do
something like this:

.. code-block:: python

    for tableObj in MyBase.myclasses():
        # generate the Resource object that uses DataTable
        resource, path, endpoint = get_resource(Resource, tableObj, Session, basepath="/")
        # add the Resource to the API object
        #print resource, path, endpoint
        api.add_resource(resource, path, endpoint=endpoint)

Example myclasses method on the MyBase class

.. code-block:: python

    class MyBase(Base):
        
        @classmethod
        def myclasses(cls):
            """
                Just returns a list of the child classes to this class
            """
            mine=[cls for cls in cls.__subclasses__()]
            return mine




Additional data such as hyperlinks can be added via DataTable.add_data, which accepts a callable that is called for
each instance. Check out the usage example below for more info.


Example
-------

**models.py**

.. code-block:: python

    class User(Base):
        __tablename__ = 'users'

        id          = Column(Integer, primary_key=True)
        full_name   = Column(Text)
        created_at  = Column(DateTime, default=datetime.datetime.utcnow)

        # Use lazy=joined to prevent O(N) queries
        address     = relationship("Address", uselist=False, backref="user", lazy="joined")

    class Address(Base):
        __tablename__ = 'addresses'

        id          = Column(Integer, primary_key=True)
        description = Column(Text, unique=True)
        user_id     = Column(Integer, ForeignKey('users.id'))

**api.py**

.. code-block:: python

    from model import Session, User, Address
    from datatables import *

    app = Flask(__name__)
    api = Api(app)
    # add User resource
    resource, path, endpoint = get_resource(Resource, User, Session, basepath="/")
    api.add_resource(resource, path, endpoint=endpoint)

    # add Address resource
    resource, path, endpoint = get_resource(Resource, Address, Session, basepath="/")
    api.add_resource(resource, path, endpoint=endpoint)


