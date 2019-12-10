from __future__ import print_function

from networks.DispNetC import DispNetC
from networks.DispNetCSS import DispNetCSS
from networks.DispNetCSRes import DispNetCSRes
from networks.DispNormNet import DispNormNet

from utils.common import logger

SUPPORT_NETS = {
        'dispnetcres': DispNetCSRes,
        'dispnetc': DispNetC,
        'dispnetcss': DispNetCSS,
        'dispnormnet':DispNormNet,
        }

def build_net(net_name):
    net  = SUPPORT_NETS.get(net_name, None)
    if net is None:
        logger.error('Current supporting nets: %s , Unsupport net: %s', SUPPORT_NETS.keys(), net_name)
        raise 'Unsupport net: %s' % net_name
    return net
