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
        # assert all((x % 2 == 0
        #            for x in [sets, block_size]))
        # assert ways is 1 or ways % 2 == 0

        self._ways = ways
        self._sets = sets
        #Block size in Bytes
        self._block_size = block_size
        self._size = self._calculate_size()
        #Get the # of bits needed to _decode the index
        self._index_bits = int(log(sets, 2))
        #Get the # of bits needed to offset into a block
        self._offset_bits = int(log(block_size, 2))
        self._set_dict = {}

        self.w_miss = 0
        self.r_miss = 0
        self.w_ops = 0
        self.r_ops = 0

    def _execute(self, operation):
        '''Takes an operation (op) tuple containing a r/w operation string, and
        a raw memory address. Incrememnts appropriate miss counts for a miss
        and updates the cache'''
        op, raw_addr = operation
        try:
            block = self[raw_addr]
        except (KeyError, IndexError):
            #Miss
            self._insert(raw_addr)
            if op.lower() == 'r':
                self.r_miss += 1
            elif op.lower() == 'w':
                self.w_miss += 1
        finally:
            if op.lower() == 'r':
                self.r_ops += 1
            elif op.lower() == 'w':
                self.w_ops += 1

    def _calculate_size(self):
        '''Calculates the cache size in bytes'''
        return self._sets * self._ways * self._block_size

    def __getitem__(self, addr):
        '''Decodes the byte address, looks for it in the cache using
        the decoded index. If the byte tag is in the index, the (tag, timestamp)
        pair is returned, otherwise throw a key error (miss).
        If the index isn't found, we throw a key error.
        '''
        tag, index, offset = self._decode(addr)
        if index in self._set_dict:
            if any(tag in pair for pair in self._set_dict[index]):
                return self._set_dict[index]
            else:
                raise IndexError("Block %s is not in set %s" % (tag, index))
        else:
            raise KeyError('Index %s not yet in cache' % index)

    def _insert(self, addr):
        '''updates the set at raw address (addr)
        using LRU replacement policy if needed'''
        tag, index, offset = self._decode(addr)
        cache_set = self._set_dict.setdefault(index, [])
        t = time()
        if len(cache_set) < self._ways:
            cache_set.append((tag, t))
        else:
            lru = max(cache_set, key=lambda (otag, otime): abs(t - otime))
            cache_set.remove(lru)
            cache_set.append((tag, t))



    def _decode(self, raw_addr):
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

    def simulate(self, tracefile):
        '''Simulates this cache on a memory trace file. tracefile should
        be a simple text file containing a memory operation on each line
        in this format:
        R 7f588cd8eb58
        W 7f588cd8eb58
        etc.
        '''
        trace = trace_read(tracefile)
        for operation in trace:
            self._execute(operation)
        misses = self.w_miss + self.r_miss
        ops = self.w_ops + self.r_ops
        total_missrate = misses / (ops * 1.0)
        write_missrate = self.w_miss / (self.w_ops * 1.0)
        read_missrate = self.r_miss / (self.r_ops * 1.0)
        results = dict(
                       cache_size=self._size,
                       ways=self._ways,
                       sets=self._sets,
                       total_missrate=total_missrate,
                       write_missrate=write_missrate,
                       read_missrate=read_missrate
                       )
        try:
            from pprint import pprint
            import json
        except ImportError:
            print results
        else:
            pprint(results)
            with open('results.txt', 'a') as out_file:
                j = json.dumps(results, indent=4)
                print >> out_file, j
        return



