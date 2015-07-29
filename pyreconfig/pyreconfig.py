from os import getcwd, environ
from os.path import expanduser, exists, join
import json

__debug = False

class pyreconfig(object):
    """
    Standard configuration glue for providing program defaults, and
     alphabetical priority over them (local config files begin with 0 or 1)

    Check configuration files:
    ./program.cfg
    ./.program
    $XDG_CONFIG_HOME and fallbacks, including OS X ~/Library/Preferences/...
    $XDG_CONFIG_DIRS and fallbacks
    ~/program.cfg
    ~/.program

    The JSON structure will resemble a nested set of 'Objects' (dict/map)
    {
    "section_name": {
        "prop 1": {"Any valid JSON": "is correct"}
        "prop 2": "Even the above nesting"
        }
    }
    """
    # json.dump(obj, fp, indent=4, sort_keys=True)
    def __init__(self):
        self.config = dict()
        self.config['z_default'] = dict()
        self.reload_configs()

    def set_default(self, section_name, section_defaults = {}):
        """
        string, dict
        none
        Install defaults for a configuration section.
        """
        self.config['z_default'][section_name] = section_defaults

    def get_defaults(self):
        """
        none
        string
        Dump defaults, intended for help output and initial config creation.
        """
        return json.dumps(self.config['z_default'], indent=4, sort_keys=True)

    def get_config(self, section_name):
        """
        string
        dict
        Return a dict of key/value configs for the requested section.
        """
        _r = dict()
        for csrc in sorted(self.config.keys(), reverse=True):
            if section_name in self.config[csrc]:
                _r.update(self.config[csrc][section_name])
        return _r

    def __load_config(self, section_name, path):
        """
        Internal function.
        """
        try:
            #self.config[section_name] = dict()
            if exists(path):
                nfp = open(path)
                self.config[section_name] = json.load(nfp)
                nfp.close()
        except (Exception,) as e:
            if __debug:
                raise e

    def reload_configs(self, name=None):
        """
        none
        none
        Reload configs.
        Note: Configuration files removed during runtime has undefined results.
        """
        home = expanduser("~")
        cwd = getcwd()

        if name is None:
            name = __name__
        nw = name + '.cfg'
        nu = '.' + name

        self.__load_config('000', join(cwd, nw))
        self.__load_config('001', join(cwd, nu))

        # XDG Directories; BSD/Linux
        if 'XDG_CONFIG_HOME' in environ:
            self.__load_config('002', join(
                    join(expanduser(environ['XDG_CONFIG_HOME']), name, nw)))
        elif exists(join(expanduser('~/Library/Preferences'), name)):
            self.__load_config('002',
                    join(expanduser('~/Library/Preferences'),
                    __name__ + '.at.github.com.plist'))
        elif 'HOME' in environ:
            self.__load_config('002', join(
                    join(expanduser(environ['HOME']), '.config', name, nw)))

        if 'XDG_CONFIG_DIRS' in environ:
            ibase = 3
            for base in environ['XDG_CONFIG_DIRS'].split(':'):
                self.__load_config('%03i' % (ibase),
                    join(expanduser(base), name, nw))
                ibase += 1
        elif exists('/etc/xdg'):
            self.__load_config('003', join('/etc/xdg', name, nw))

        self.__load_config('110', join(home, nw))
        self.__load_config('111', join(home, nu))
