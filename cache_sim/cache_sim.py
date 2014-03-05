from trace_read import trace_read

BLOCK_SIZE = 32 #Bytes
MAX_ADDR = 0xFFFFFFFFFFFF
ADDRESS_SIZE = 48



class Cache(object):
    """The class implements a cache. Use the cache's simulate function
    to observe its performance.

    :param: assoc = associativity of the cache.
    :type: int
    :param: sets = number of sets in the cache.
    :type: int
    :param: block_size size of one cache blocks
    :type: int
    """
    def __init__(self, assoc=1, sets=128, block_size=32, blocks=128):
        assert all((x % 2 == 0
                   for x in [sets, block_size, blocks]))
        assert assoc is 1 or assoc % 2 == 0

        self._assoc = assoc
        self._sets = sets
        self._block_size = block_size
        self._size = self._calculate_size()
        self._index_bits = len(bin(sets)[2:])
        self._offset_bits = 5

        self.w_hits = 0
        self.r_hits = 0
        self.n_ops = 0

    def _read_op(self, addr):
        pass

    def _write_op(self, addr):
        pass

    def _calculate_size(self):
        '''Calculates the cache size in bytes'''
        return self._sets * self._assoc * self._block_size

    def decode(self, raw_addr):
        '''returns the tag, index, and offset for a raw address'''
        addr_bits = bin(int(raw_addr, 16))[2:]
        addr_bits = addr_bits.zfill(ADDRESS_SIZE)
        tag_end = ADDRESS_SIZE - self._offset_bits - self._index_bits

        tag = addr_bits[:tag_end]
        index = addr_bits[tag_end:tag_end+self._index_bits]
        offset = addr_bits[-self._offset_bits:]
        assert len(tag + index + offset) == len(addr_bits)
        return (tag, index, offset)

    def simulate(tracefile):
        '''Simulates this cache on a memory trace file. tracefile should
        be a simple text file containing a memory operation on each line
        in this format:
        R 7f588cd8eb58
        W 7f588cd8eb58
        etc.
        '''
        trace = trace_read(tracefile)



