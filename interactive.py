from cache_sim import cache_sim
from pprint import pprint

traces = ['mcf_memref.out', 'gcc_memref.out']
caches = []

def main():
    print 'Welcome to the ineractive shell. type "help" for a list of commands'
    inp = raw_input('>').lower()
    while inp != 'q':
        if inp == 'help':
            print_help()
        elif inp == 'n':
            print "Ok, let's create a cache."
            n_sets = int(raw_input('number of sets?: '))
            n_ways = int(raw_input('number of ways?: '))
            try:
                caches.append(cache_sim.Cache(n_ways=n_ways, n_sets=n_sets))
            except AssertionError:
                print 'sorry, something went wrong with those parameters. try again'
        elif inp == 's':
            print "Which cache would you like to simulate?: "
            for i, c in enumerate(caches):
                print '%d\tcache: sets(%d) ways(%d)' % (i, c.n_sets, c.n_ways)
            choice = int(raw_input('>'))
            print '-'*50
            for i, m in enumerate(traces):
                print '%d\t%s\n' % (i, m)
            f = int(raw_input('which memory trace would you like to simulate?: '))
            print 'simulating...'
            pprint(caches[choice].simulate(traces[f]))
        inp = raw_input('>').lower()

def print_help():
    print '''
    help    prints the help message
    q       quits the interactive shell
    n       creates a new cache
    s       simulate a cache
    '''

if __name__ == '__main__':
    main()
