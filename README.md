#cache\_sim

##A cache simulator and analysis tool written in python. Created for a Computer Architecture class at Edinburgh Uni

##Results
If you're just interested in the simulation results, check out the two .json files mcf\_results.json and gcc\_results.json.

###Usage
The quickest way to start simulating your own caches is to run the interactive.py script. It will provide a number of prompted command line switches for creating and simulating caches.

If you'd like to get a little more involved, import the Cache class from cache\_sim, and create a cache with c = Cache(n\_sets=128, n\_ways=1) and simulate it with c.simulate('mcf\_memref.out').

To quickly create all of the caches specified in the coursework description, run this code:

    from cache_sim import test_caches
    caches = test_caches()

to get a list of all the caches. Alternatively, just do this:

    from cache_sim import simulate_all
    simulate_all('mcf_memref.out', 'mcf_results.json2')

##Structure
Simulation is done using a cache class's "execute" method, which looks for a raw address (a 12 digit hex string) in its sets, and logs misses when they occur. If you'd like to see how things are working, you can break the process into steps. i.e.

    c.\_decode('FFFFFFFFFFFF')

returns ('000011111111111111111111111111111111', '1111111', '11111')

this is the tag, index, and block offset used to find a set/block in the cache.

    c.\_insert('FFFFFFFFFFFF')

inserts a block into the cache.

    c['FFFFFFFFFFFF'] 

will return the timestamp for the block you just inserted.

    c['FFFFFF000000']

will throw an exception because that block isn't in the cache.

However,

    c['FFFFFFFFFFE']

won't, because we've already loaded that block.
You get the idea.
