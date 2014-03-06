from trace_read import trace_read
import sys
from math import log
from time import time

BLOCK_SIZE = 32 #Bytes
MAX_ADDR = 0xFFFFFFFFFFFF
ADDRESS_SIZE = 48



class Cache(object):
    """The class implements a cache. Use the cache's simulate function
    to observe its performance.

    :param: ways = associativity of the cache.
    :type: int
    :param: sets = number of sets in the cache.
    :type: int
    :param: block_size size of one cache blocks
    :type: int
    """
    def __init__(self, ways=1, sets=128, block_size=32):
        assert all((x % 2 == 0
                   for x in [sets, block_size]))
        assert ways is 1 or ways % 2 == 0

        self._ways = ways
        self._sets = sets
        #Block size in Bytes
        self._block_size = block_size
        self._size = self._calculate_size()
        #Get the # of bits needed to decode the index
        self._index_bits = int(log(sets, 2))
        #Get the # of bits needed to offset into a block
        self._offset_bits = int(log(block_size, 2))
        self._blocks = {}

        self.w_hits = 0
        self.r_hits = 0
        self.n_ops = 0

    def _execute(self, operation):
        '''Takes an operation (op) tuple containing a r/w operation string, and
        a raw memory address. Incrememnts appropriate hit counts for a hit,
        updates the cache on a miss'''
        op, addr = operation
        try:
            result = self[addr]
        except (KeyError, IndexError):
            self._insert(addr)
        else:
            if op.lower() == 'r':
                self.r_hits += 1
            elif op.lower() == 'w':
                self.w_hits += 1
        finally:
            self.n_ops +=1

    def _calculate_size(self):
        '''Calculates the cache size in bytes'''
        return self._sets * self._ways * self._block_size

    def __getitem__(self, addr):
        '''Decodes the byte address, looks for it in the cache using
        the decoded index. If the byte tag is in the index, the (tag, timestamp)
        pair is returned, otherwise throw a key error (miss).
        If the index isn't found, we throw a key error.
        '''
        tag, index, offset = self.decode(addr)
        if index in self._blocks:
            if any(tag in pair for pair in self._blocks[index]):
                return self._blocks[index]
            else:
                raise IndexError("Block %s is not in set %s" % (tag, index))
        else:
            raise KeyError('Index %s not yet in cache' % index)

    def _insert(self, addr):
        '''updates the set at raw address (addr)
        using LRU replacement policy if needed'''
        tag, index, offset = self.decode(addr)
        cache_set = self._blocks.setdefault(index, [])
        t = time()
        if len(cache_set) < self._ways:
            cache_set.append((tag, t))
        else:
            lru = max(cache_set, key=lambda (otag, otime): abs(t - otime))
            cache_set.remove(lru)
            cache_set.append((tag, t))



    def decode(self, raw_addr):
        assert type(raw_addr) is str
        '''returns the tag, index, and offset for a raw address'''
        addr_bits = bin(int(raw_addr, 16))[2:]
        addr_bits = addr_bits.zfill(ADDRESS_SIZE)
        assert len(addr_bits) == ADDRESS_SIZE
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



