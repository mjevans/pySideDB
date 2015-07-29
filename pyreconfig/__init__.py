try:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
except (Exception, ) as e:
    try:
        import pkg_resources
        pkg_resources.declare_namespace(__name__)
    except (Exception, ) as e:
        pass

from . import pyreconfig

__version__ = '0.0.1-alpha1'

__author__ = 'Michael J. Evans <mjevans1983@gmail.com>'

__all__ = ['pyreconfig', ]

__license__ = 'LGPL 3+'
