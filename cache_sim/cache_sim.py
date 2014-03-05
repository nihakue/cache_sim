from trace_read import trace_read

BLOCK_SIZE = 0xFF
MAX_ADDR = 0xFFFFFFFFFFFF

class Cache(object):
    """The class implements a cache. Use the cache's simulate function
    to observe its performance.

    :param: assoc = associativity of the cache.
    :type: int
    :param: sets = number of sets in the cache. This in part determines the size of the cache.
    :type: int
    """
    def __init__(self, assoc, sets):
        self._assoc = assoc
        self._sets = sets
        self._kb = self._calculate_size()
        self.w_hits = 0
        self.r_hits = 0
        self.n_ops = 0

    def _read_op(self, addr):
        pass

    def _write_op(self, addr):
        pass

    def _calculate_size(self):
        return 4 * self._sets

    def _decode(self, raw_addr):
        '''returns the tag, index, and offset for a raw address'''


    def simulate(tracefile):
        '''Simulates this cache on a memory trace file. tracefile should
        be a simple text file containing a memory operation on each line
        in this format:
        R 7f588cd8eb58
        W 7f588cd8eb58
        etc.
        '''
        trace = trace_read(tracefile)



