import sys
import psycopg2

if len(sys.argv) != 2:
    raise(RuntimeError("Incorrect number of arguments: Exactly one required"))

gcfg_sysuser = sys.argv[-1:][0]

print("Attempting to create pysidedb_devdb and grant access to system user '%s'" % (gcfg_sysuser))

try:
    pg = psycopg2.connect("user=postgres")

    pg.autocommit = True # Required for CREATE DATABASE, probably for all CREATE statements (except temp tables).
                     # According to the documentation, this should ALSO be SET FOR long running threads (which should be readers).
                     # Note to self: set this true between transaction batches.

    pc = pg.cursor()

    pc.execute("CREATE DATABASE pysidedb_devdb;")

    # pc.commit()

    for notice in pg.notices:
        print("CREATE DATABASE: %s" % (str(notice)), file=sys.stderr)

    pg.close()
except (psycopg2.Error, ) as e:
    print("Result: %s: %s" % (str(e.pgcode), e.pgerror), file=sys.stderr)




try:
    pg = psycopg2.connect("dbname=pysidedb_devdb user=postgres")

    pg.autocommit = True # Required for CREATE DATABASE, probably for all CREATE statements (except temp tables).

    pc = pg.cursor()

    pc.execute("""
    CREATE SCHEMA common;
    CREATE SCHEMA production;
    CREATE SCHEMA shipping;
    --
    CREATE TABLE common.hlv (id SERIAL PRIMARY KEY, val TEXT, ord INTEGER);
    CREATE VIEW common.hlv_list AS SELECT id, val FROM common.hlv ORDER BY ord ASC, val ASC;
    --
    CREATE TABLE common.customer_order (customer_order_id SERIAL PRIMARY KEY, manual_address TEXT, more_columns TEXT, note TEXT);
    CREATE VIEW common.customer_order_list AS SELECT customer_order_id AS id, CONCAT_WS(E'\n', more_columns, note) AS val FROM common.customer_order ORDER BY customer_order_id ASC;
    -- I prefer 'id' form my self, but some have a preference for tablename_id --
    --
    CREATE TABLE production.workflow (id SERIAL PRIMARY KEY, open_order BIGINT, note TEXT);
    CREATE VIEW production.workflow_open_order_list AS SELECT * FROM common.customer_order_list;
    --
    CREATE TABLE shipping.fulfillment (id SERIAL PRIMARY KEY, shipped BIGINT, ship_address TEXT, ship_status TEXT, ship_track TEXT, ship_order BIGINT, note TEXT);
    CREATE VIEW shipping.ship_order_list AS SELECT * FROM common.customer_order_list;
    CREATE VIEW shipping.fulfillment_shiped_list AS SELECT id, val FROM common.hlv ORDER BY ord ASC, val ASC;
    --
    CREATE USER {0} WITH LOGIN;
    GRANT ALL ON DATABASE pysidedb_devdb TO {0};
    GRANT ALL ON ALL TABLES IN SCHEMA common TO {0};
    GRANT ALL ON ALL TABLES IN SCHEMA production TO {0};
    GRANT ALL ON ALL TABLES IN SCHEMA shipping TO {0};
    GRANT ALL ON ALL SEQUENCES IN SCHEMA common TO {0};
    GRANT ALL ON ALL SEQUENCES IN SCHEMA production TO {0};
    GRANT ALL ON ALL SEQUENCES IN SCHEMA shipping TO {0};
    """.format(gcfg_sysuser,))

    for notice in pg.notices:
        print("POPULATE DATABASE: %s" % (str(notice)), file=sys.stderr)
    # pc.commit()

    pg.close()

except (psycopg2.Error, ) as e:
    print("Result: %s: %s" % (str(e.pgcode), e.pgerror), file=sys.stderr)