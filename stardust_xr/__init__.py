from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution('stardust-py').version
except DistributionNotFound:
    __version__ = '(local)'
