import pyreconfig
import pydbreflection

# reconfig base
cfg = pyreconfig.pyreconfig.pyreconfig()
# reconfig 'customer'
db = pydbreflection.pydbreflection.get_adapter()
# load defaults from custoemr
cfg.set_default('db',db.get_config_defaults())

# Write defauults as config; normally done only if requested
open("test.cfg", "w").write(cfg.get_defaults())

# load on disk config
cfg.reload_configs()
# reconfigure with current config
db.config = cfg.get_config('db')

# FIXME # Read config table /from/ database

# Then reconfigure /again/
db.config = cfg.get_config('db')

db.update_reflection()

import pprint
pprint.pprint(db.schema)
