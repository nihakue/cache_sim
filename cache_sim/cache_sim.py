from trace_read import trace_read
import sys
from math import log
from time import time
import pdb



class Cache(object):
    """The class implements a cache. Use the cache's simulate function
    to observe its performance.

    :param: n_ways = associativity of the cache.
    :type: int
    :param: n_sets = number of sets in the cache.
    :type: int
    :param: block_size size of one cache blocks
    :type: int
    :param: address_size number of bits in a raw address
    """
    def __init__(self, n_ways=1, n_sets=128, block_size=32, address_size=48):
        # assert all((x % 2 == 0
        #            for x in [n_sets, block_size]))
        # assert n_ways is 1 or n_ways % 2 == 0

        self._n_ways = n_ways
        self._n_sets = n_sets
        self._address_size = address_size
        #Block size in Bytes
        self._block_size = block_size
        self._size = self._calculate_size()
        #Get the # of bits needed to _decode the index
        self._index_bits = int(log(n_sets, 2))
        #Get the # of bits needed to offset into a block
        self._offset_bits = int(log(block_size, 2))
        self._sets = {}

        self.w_miss = 0
        self.r_miss = 0
        self.w_ops = 0
        self.r_ops = 0

    def _execute(self, operation):
        '''Takes an operation tuple containing a r/w indicator and
        a raw memory address. Updates the cache and increments appropriate miss counts in the event of a miss.
        '''
        op, raw_addr = operation
        try:
            block = self[raw_addr]
        except (KeyError, IndexError):
            #Must have been a miss. Update the cache
            self._insert(raw_addr)
            if op.lower() == 'r':
                self.r_miss += 1
            elif op.lower() == 'w':
                self.w_miss += 1
        finally:
            #Whether or not we miss
            if op.lower() == 'r':
                self.r_ops += 1
            elif op.lower() == 'w':
                self.w_ops += 1

    def _calculate_size(self):
        '''Calculates the cache size in bytes'''
        return self._n_sets * self._n_ways * self._block_size

    def __getitem__(self, addr):
        '''Looks for a word in the cache using
        the decoded index and block tag. If the block tag is in the set,
        it is returned with an updated timestamp,
        otherwise throw a key error (miss).
        If the index isn't found, we throw a key error (cold miss).
        '''
        tag, index, offset = self._decode(addr)
        if index in self._sets:
            cache_set = self._sets[index]
            if tag in cache_set:
                cache_set[tag] = time()
                return cache_set
            else:
                raise IndexError("Block %s is not in set %s" % (tag, index))
        else:
            raise KeyError('Index %s not yet in cache' % index)

    def _insert(self, addr):
        '''updates the set with the block containing raw address (addr)
        using LRU replacement policy if needed.'''
        tag, index, offset = self._decode(addr)
        #If we've never seen the index before, create an empty dict
        cache_set = self._sets.setdefault(index, {})
        t = time()
        if len(cache_set) < self._n_ways:
            #insert/update timestamp of the block
            cache_set[tag] = t
        else:
            #get the LRU block in the set by comparing timestamps to t
            lru = max(cache_set.iterkeys(),
                      key=lambda k: abs(cache_set[k] - t))
            cache_set.pop(lru)
            cache_set[tag] = t

    def _decode(self, raw_addr):
        '''returns the tag, index, and offset for a raw address'''
        assert type(raw_addr) is str
        addr_bits = bin(int(raw_addr, 16))[2:]
        #Left pad 0s till it's the right number of bits
        addr_bits = addr_bits.zfill(self._address_size)
        #Check that it's not too long
        assert len(addr_bits) == self._address_size

        tag_end = self._address_size - self._offset_bits - self._index_bits
        tag = addr_bits[:tag_end]
        index = addr_bits[tag_end:tag_end+self._index_bits]
        offset = addr_bits[-self._offset_bits:]
        assert len(tag + index + offset) == len(addr_bits)
        return (tag, index, offset)

    def _reset(self):
        self._sets = {}
        self.w_ops = 0
        self.r_ops = 0
        self.r_miss = 0
        self.w_miss = 0

    def simulate(self, tracefile, verbose=False):
        '''Simulates this cache on a memory trace file. tracefile should
        be a simple text file containing a memory operation on each line
        in this format:
        R 7f588cd8eb58
        W 7f588cd8eb58
        etc.
        '''
        #Reset cache if it's been run before
        if self._sets:
            self._reset()

        trace = trace_read(tracefile)
        t = time()
        for operation in trace:
            self._execute(operation)
        dt = time() - t

        misses = self.w_miss + self.r_miss
        ops = self.w_ops + self.r_ops
        total_missrate = misses / (ops * 1.0)
        write_missrate = self.w_miss / (self.w_ops * 1.0)
        read_missrate = self.r_miss / (self.r_ops * 1.0)
        exec_time = dt

        #Do some cursory checks to verify sane results. Doesn't
        #prove that they're valid, just that they could be.

        assert all([len(s) <= self._n_ways
                   for s in self._sets.itervalues()])
        assert ops == len(trace)

        results = dict(
                       cache_size=self._size,
                       n_ways=self._n_ways,
                       n_sets=self._n_sets,
                       total_missrate=total_missrate,
                       write_missrate=write_missrate,
                       read_missrate=read_missrate,
                       trace_file=tracefile,
                       exec_time=exec_time
                       )
        if verbose:
            try:
                from pprint import pprint
                import json
            except ImportError:
                print results
            else:
                pprint(results)
            finally:
                print 'misses: %d, ops: %d' % (misses, ops)
        return results

def test_caches():
    m_range = [1, 2, 4, 8, 16]
    n_ways = [1, 2, 4, 8, 16]
    caches = [Cache(n_sets=128/k * i, n_ways=k) for i in m_range for k in n_ways]
    return caches

def simulate_all(infile, outfile):
    import json
    caches = test_caches()
    results = [c.simulate(infile) for c in caches]
    with open(outfile, 'w') as o:
        j = json.dump(results, o, indent=4)
