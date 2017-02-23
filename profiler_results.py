import pstats

p = pstats.Stats('k2profile.txt')
p.strip_dirs().sort_stats(2).print_stats()
