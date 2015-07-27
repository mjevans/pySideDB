import psycopg2
from . import pydbreflection

class DBA2(pydbreflection.PyDBReflection_base):
    def __init__(self, connect, reflect = True):
        self.connect = connect
        self.schema = {}
        self.table_ref = {}
        if True == reflect:
            self.refresh_reflection()
        super().__init__(connect = connect, db_type = "psycopg2")
    def get_conn(self):
        try:
            pg = psycopg2.connect(self.connect)
            pg.autocommit = True
            """Required for CREATE DATABASE, probably for all CREATE statements

            Documentation states that .autocomit = True releases server resources

            Writers should set this True between transactions.
            Readers should be set to True."""
            return pg
        except (Exception,) as e:
            raise e
    def refresh_columns(self):
        try:
            pg = self.get_conn()
            pc = pg.cursor()

            # table_catalog = 'db' AND
            pc.execute("""SELECT table_schema,
                                 table_name,
                                 column_name,
                                 is_nullable,
                                 data_type
                          FROM information_schema.columns
                          WHERE table_schema NOT IN ('information_schema',
                                                     'pg_catalog');""")
            self.schema = {}
            self.table_ref = {}
            for (schema, table, column, canhasnull, dtype) in pc:
                if schema not in self.schema:
                    self.schema[schema] = {}
                if table not in self.schema[schema]:
                    self.schema[schema][table] = {column: {}}
                if table not in self.table_ref:
                    self.table_ref[table] = {}
                st = '.'.join((schema, table))
                if st not in self.table_ref[table]:
                    self.table_ref[table][st] = st
                if "YES" == canhasnull:
                    cnull = True
                else:
                    cnull = False
                # FIXME: how does py3 psycopg2 handle pg json/jsonb/XML?
                if   dtype in ('bigint', 'bigserial', 'integer',
                               'int8', 'serial8', 'int', 'int4',
                               'smallint', 'int2', 'smallserial',
                               'serial2', 'serial', 'serial4'):
                    ctype = 'integer'
                elif dtype in ('bit', 'bit varying', 'varbit', 'bytea'):
                    ctype = 'binary'
                elif dtype in ('character', 'char', 'character varying',
                               'varchar', 'text'):
                    ctype = 'text'
                elif dtype in ('double precision', 'double', 'float8',
                               'real', 'float', 'float4'):
                    ctype = 'float'
                elif dtype in ('datetime', 'timestamp',
                               'timestamptz',
                               'timestamp out time zone',
                               'timestamp without time zone'):
                    ctype = 'datetime'
                elif dtype in ('date',):
                    ctype = 'date'
                elif dtype in ('time with time zone', 'time',
                               'time without time zone', 'timetz'):
                    ctype = 'time'
                elif dtype in ('interval',):
                    ctype = 'interval'
                elif dtype in ('tsvector',):
                    ctype = 'tsvector'
                elif dtype in ('uuid',):
                    ctype = 'uuid'
                else:
                    ctype = 'other'
                self.schema[schema][table]['column'][column] = {
                    'null': cnull, 'type': ctype}
            pg.close()
            # super().refresh_columns()
        except (psycopg2.Error, ) as e:
            print("Result: %s: %s" % (str(e.pgcode), e.pgerror), file=sys.stderr)
