from os import getcwd, environ
from os.path import expanduser, exists, join
import json

__debug = False

class reconfig(object):
    """
    Check configuration files:
    ./program.cfg
    ./.program
    $XDG_CONFIG_HOME and fallbacks, including OS X ~/Library/Preferences/...
    $XDG_CONFIG_DIRS and fallbacks
    ~/program.cfg
    ~/.program
    """
    # json.dump(obj, fp, indent=4, sort_keys=True)
    def __init__(self):
        self.__config = dict()
        self.__config['z_default'] = dict()
        self.reload_configs()

    def set_default(self, section_name, section_defaults = {}):
        """
        string, dict
        none
        Install defaults for a configuration section.
        """
        self.__config['z_default'][section_name] = section_defaults

    def get_defaults(self):
        """
        none
        string
        Dump defaults, intended for help output and initial config creation.
        """
        return json.dumps(self.__config['z_default'], indent=4, sort_keys=True)

    def get_config(self, section_name):
        """
        string
        dict
        Return a dict of key/value configs for the requested section.
        """
        _r = dict()
        for csrc in sorted(self.__config.keys(), reverse=True):
            if section_name in self.__config[csrc]:
                _r.update(self._config[csrc][section_name])
        return _r

    def __load_config(self, section_name, path):
        """
        Internal function.
        """
        try:
            #self.__config[section_name] = dict()
            if exists(path):
                nfp = open(path)
                self.__config[section_name] = json.load(nfp)
                nfp.close()
        except (Exception,) as e:
            if __debug:
                raise e

    def reload_configs(self):
        """
        none
        none
        Reload configs.
        Note: Configuration files removed during runtime has undefined results.
        """
        home = expanduser("~")
        cwd = getcwd()
        nw = __name__ + '.cfg'
        nu = '.' + __name__

        self.__load_config('000', join(cwd, nw))
        self.__load_config('001', join(cwd, nu))

        # XDG Directories; BSD/Linux
        if 'XDG_CONFIG_HOME' in environ:
            self.__load_config('002', join(tdir,
                    join(expanduser(environ['XDG_CONFIG_HOME']), __name__, nw)))
        elif exists(join(expanduser('~/Library/Preferences'), __name__)):
            self.__load_config('002',
                    join(expanduser('~/Library/Preferences'),
                    __name__ + '.at.github.com.plist'))
        elif 'HOME' in environ:
            self.__load_config('002', join(tdir,
                    join(expanduser(environ['HOME']), '.config', __name__, nw)))

        if 'XDG_CONFIG_DIRS' in environ:
            ibase = 3
            for base in environ['XDG_CONFIG_DIRS'].split(':'):
                self.__load_config('%03i' % (ibase),
                    join(expanduser(base), __name__, nw))
                ibase += 1
        elif exists('/etc/xdg'):
            self.__load_config('003', join('/etc/xdg', __name__, nw))

        self.__load_config('110', join(home, nw))
        self.__load_config('111', join(home, nu))
