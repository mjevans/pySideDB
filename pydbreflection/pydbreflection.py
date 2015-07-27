from importlib import import_module

glbl_pydbreflection_adapters = dict() #None

def get_adapter(connect = None, db_type = None, config = None):
        if config is None:
            config = PyDBReflection_base.get_config_defaults()['pydbreflection']
        else:
            config = config
        if connect is not None:
            config['connect'] = connect
        if db_type is not None:
            config['db_type'] = db_type
        db_type = config['db_type']
        if db_type not in glbl_pydbreflection_adapters:
            glbl_pydbreflection_adapters[db_type] = import_module(
                '..adapter_%s' % (db_type), __name__ )
        return glbl_pydbreflection_adapters[db_type].DBA2

class PyDBReflection_base(object):
    """
    Introspect the structure of the database, and present a more end user
    friendly way of modifying the structure (TODO) and data.
    """
    def __init__(self, connect = None, db_type = None, config = None):
        if config is None:
            self.config = self.get_config_defaults()['pydbreflection']
        else:
            self.config = config
        if connect is not None:
            self.config['connect'] = connect
        if db_type is not None:
            self.config['db_type'] = db_type
        self.last_reflection = 0.0
    #def refresh_columns(self):
    #    # FIXME: Remove if no universal callbacks are desired for this function.
    #    pass
    def update_reflection(self, force_refresh = False):
        if force_refresh or (self.last_reflection + self.config['cache_period']):
            self.refresh_columns()
        for schema, table in [(schema, table) for
                            schema in self.schema for
                            table in self.schema[schema]]:
            guess_pk = None
            guess_ts = None
            text_last = None
            text_count = 0
            for cname, column in self.schema[schema][table]['column'].items():
                if guess_pk is None and self.test_is_this_pk(schema = schema,
                                                             table = table,
                                                             column = cname):
                    guess_pk = cname
                if guess_ts is None and column['type'] == 'tsvector':
                    guess_ts = cname
                if column['type'] == 'text':
                    text_last = cname
                    text_count += 1
            # FIXME: Magic number, 7 columns, should be a config.
            # Default is 6, id, text, sort_order, tsvector... + 2 misc
            if (text_count == 1 and guess_pk is not None and
                        len(self.schema[schema][table]['column']) <= 6):
                self.schema[schema][table]['table_type_guess'] = 'enumeration'
            elif guess_pk is not None:
                self.schema[schema][table]['table_type_guess'] = 'table'
            else:
                self.schema[schema][table]['table_type_guess'] = 'unknown'

            # FIXME: Config in DB, update defaults? -- at outermost layer
    @staticmethod
    def get_config_defaults():
        return { 'pydbreflection': {
            #'': '',
            'db_type':      'psycopg2',
            'connect':      'dbname=pysidedb_devdb',
            'cache_period': 1800
        }}
    @staticmethod
    def test_is_this_pk(column, table = '', schema = ''):
        return (column == 'id' or column == 'pk' or
                column == '_'.join(table, 'id') or
                column == '_'.join(table, 'pk') or
                column == '_'.join(schema, table, 'id') or
                column == '_'.join(schema, table, 'pk'))
