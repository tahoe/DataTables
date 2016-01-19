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

Using Datatables is simple. Construct a DataTable instance by passing it your request parameters (or another dict-like
object), your model class, a base query and a set of columns. The columns list can contain simple strings which are
column names, or tuples containing (datatable_name, model_name), (datatable_name, model_name, filter_function) or
(datatable_name, filter_function).

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


