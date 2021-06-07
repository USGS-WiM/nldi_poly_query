''' NLDI toolset to delineate drainage basins and trace raindrop paths. '''

from .flowtool_functions import splitcatchment, flowtrace

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
