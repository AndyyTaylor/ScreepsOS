
import config  # noqa
from defs import *  # noqa
from extends import *  # noqa

from framework.kernel import Kernel

__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

kernel: Kernel = Kernel()
js_global.kernel = kernel

RawMemory.setActiveForeignSegment('LeagueOfAutomatedNations', 99)

def main():
    kernel.start()
    kernel.run()
    kernel.shutdown()


module.exports.loop = main
