from collections import namedtuple
from sqlalchemy import and_, or_
import inspect
from querystring_parser import parser
from flask import request
import views


def get_resource(Resource, Table, Session, basepath="/"):
    """ Return a flask-restful datatables resource for SQLAlchemy

        This function returns a class subclassed from Flask-Restless Resource
        that is set up for GET only restful requests prepared for datatables
        and enhanced with Flask-Restless filtering

        Use this function inside your flask-restful app to create
        datatables endpoints for your SA tables

        ARGS:
            Resource    (class):    Flask-Restful Resource
            Table       (class):    SA Table class
            Session     (inst):     SA Session instance
            basepath    (str):      Base path to put endpoint

        EXAMPLE:
            Assuming you already have your SA Session object as Session

            app = Flask(__name__)
            api = Api(app)
            resource, path, endpoint = get_resource(Resource, tableObj, Session, basepath="/")
            api.add_resource(resource, path, endpoint=endpoint)

        
    """
    class TmpResource(Resource):
        def get(self):
            # parse the url args into a dict
            parsed = parser.parse(request.query_string)

            # column names for this table
            dtcols = get_columns(Table, parsed)
            #for col in dtcols:
            #    print col

            # pre build the query so we can add filters to it here
            query = Session.query(Table)

            # check if mark is filtering the rows by a username or whatever
            if 'q' in parsed.keys():
                query = views.search(Session, Table, parsed)
                #query = search.search(Session, Table, query, parsed['q'])

            # get our DataTable object
            dtobj = DataTable( parsed, Table, query, dtcols)
            # return the query result in json

            return dtobj.json()
    # return stuff that can be passed to api.add_resource
    return (TmpResource, '%s%s' % (basepath,Table.__tablename__), '%s%s' % (basepath,Table.__tablename__))



def get_columns(Table, parsed):
    """
        Helper function that just builds the tuples datatables needs for the columns
    """
    # column names for this table
    dtcols = []
    # put them in, it's just a list of (col_name, col_name)
    for col in parsed['columns'].values():
        col = col['data']
        colname = col
        if col:
            if '__' in col:
                col = col.replace('__', '.')
            dtcols.append((colname, col, lambda i: "{}".format(i)))
    return dtcols



BOOLEAN_FIELDS = (
    "search.regex", "searchable", "orderable", "regex"
)


DataColumn = namedtuple("DataColumn", ("name", "model_name", "filter"))


class DataTablesError(ValueError):
    pass


class DataTable(object):
    def __init__(self, params, model, query, columns):
        self.params = params
        self.model = model
        self.query = query
        self.data = {}
        self.columns = []
        self.columns_dict = {}
        self.search_func = lambda qs, s: qs

        for col in columns:
            name, model_name, filter_func = None, None, None

            if isinstance(col, DataColumn):
                d = col
                self.columns.append(d)
            elif isinstance(col, tuple):
                # col is either 1. (name, model_name), 2. (name, filter) or 3. (name, model_name, filter)
                if len(col) == 3:
                    name, model_name, filter_func = col
                elif len(col) == 2:
                    # Work out the second argument. If it is a function then it's type 2, else it is type 1.
                    if callable(col[1]):
                        name, filter_func = col
                        model_name = name
                    else:
                        name, model_name = col
                else:
                    raise ValueError("Columns must be a tuple of 2 to 3 elements")
                d = DataColumn(name=name, model_name=model_name, filter=filter_func)
                self.columns.append(d)
            else:
                # It's just a string
                name, model_name = col, col
                d = DataColumn(name=name, model_name=model_name)
                self.columns.append(d)
            self.columns_dict[d.name] = d

        # get only unique relationships to join
        # fix for when there are multiple columns within the same joined table
        # only eliminates warnings but still...
        seencols = []
        for column in (col for col in self.columns if "." in col.model_name):
            joincol = column.model_name.split(".")[0]
            if joincol not in seencols:
                self.query = self.query.join(joincol)
                seencols.append(joincol)


    @staticmethod
    def coerce_value(key, value):
        try:
            return int(value)
        except ValueError:
            if key in BOOLEAN_FIELDS:
                return value == "true"

        return value

    def get_integer_param(self, param_name):
        if param_name not in self.params:
            raise DataTablesError("Parameter {} is missing".format(param_name))

        try:
            return int(self.params[param_name])
        except ValueError:
            raise DataTablesError("Parameter {} is invalid".format(param_name))

    def add_data(self, **kwargs):
        self.data.update(**kwargs)

    def json(self):
        try:
            return self._json()
        except DataTablesError as e:
            return {
                "error": str(e)
            }

    def get_column(self, column):
        if "." in column.model_name:
            column_path = column.model_name.split(".")
            relationship = getattr(self.model, column_path[0])
            model_column = getattr(relationship.property.mapper.entity, column_path[1])
        else:
            model_column = getattr(self.model, column.model_name)

        return model_column

    def searchable(self, func):
        self.search_func = func

    def _json(self):
        draw = self.get_integer_param("draw")
        start = self.get_integer_param("start")
        length = self.get_integer_param("length")

        columns = self.params["columns"]
        ordering = self.params["order"]
        search = self.params["search"]

        query = self.query
        total_records = query.count()

        if search.get("value", None):
            # unicode that value we are going to page filter with
            valuestr = '%%%s%%' % str(search["value"])

            # this builds a list of .like() comparisons for the
            # value passed and every column so it's a global search
            orlist = []
            for searchcol in self.columns:
                model_column = self.get_column(searchcol)
                orlist.append(model_column.like(unicode(valuestr)))

            # modify the query then return it
            query = query.filter(and_(or_(*orlist)))


        for order in ordering.values():
            direction, column = order["dir"], order["column"]
            column = int(column)

            if column not in columns:
                raise DataTablesError("Cannot order {}: column not found".format(column))

            if not columns[column]["orderable"]:
                continue

            column_name = columns[column]["data"]
            column = self.columns_dict[column_name]

            model_column = self.get_column(column)

            if isinstance(model_column, property):
                raise DataTablesError("Cannot order by column {} as it is a property".format(column.model_name))

            query = query.order_by(model_column.desc() if direction == "desc" else model_column.asc())

        filtered_records = query.count()
        query = query.slice(start, start + length)

        retval = {
            "draw": draw,
            "recordsTotal": total_records,
            "recordsFiltered": filtered_records,
            "data": [
                self.output_instance(instance) for instance in query.all()
            ]
        }
        #print retval
        return retval

    def output_instance(self, instance):
        returner = {
            key.name.replace('.', '__'): self.get_value(key, instance) for key in self.columns
        }

        if self.data:
            returner["DT_RowData"] = {
                k: v(instance) for k, v in self.data.items()
            }

        return returner

    def get_value(self, key, instance):
        attr = key.model_name
        if "." in attr:
            tmp_list=attr.split(".")
            attr=tmp_list[-1]
            for sub in tmp_list[:-1]:
                instance = getattr(instance, sub)

        if key.filter is not None:
            r = key.filter(getattr(instance, attr))
        else:
            r = getattr(instance, attr)

        return r() if inspect.isroutine(r) else r



