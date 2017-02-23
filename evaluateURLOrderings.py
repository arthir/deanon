# input: clicks of anon'ed ppl, function to give an ordering of urls
# output: list of # urls used, cost, # ppl deanon'ed

# -------------------------------------------------------------------------------------

import csv
import sys
sys.path.append('/home/arthi/Documents/SocialNetworks/Deanonymization/')
import utils as utils
import ordering as ordering
import datetime

# Parameter

click_file = "nyt_urls_clicked_ctr_0.01.txt"
posts_file = "../../Curation/postingFilteringLawRawData.txt"
graph_file = "../../Curation/NYTIMES_FULL_PARSED.sorted.txt"

#results_file = "nyt_random_ordering_results.txt"
#ordering_function = ordering.randomOrdering


ordering_name = sys.argv[1]
results_file = sys.argv[2]
ordering_function = eval(sys.argv[3]) # in general, this is bad since a random user could supply arbitrary code
k = int(sys.argv[4]) # max size of tuples that we keep

print "start: ",  datetime.datetime.now()
# read clicks [user] -> urls
clicks_by_user = dict()
real_ids = dict() # [fake id] -> real id
with open(click_file, "rb") as f:
    for line in f:
        fields = line.strip().split("\t")
        user = fields[2]
        real_user = fields[0]
        url = fields[1]
        if user not in clicks_by_user:
            clicks_by_user[user] = set()
        clicks_by_user[user].add(url)
        real_ids[user] = real_user
#print "done reading clicks"

# read posts
posters_by_url = dict() # [url] -> (posters)
#urls = utils.getURLs(posts_file, remove_trailing = True) # [poster] -> (urls)
with open(posts_file, "rb") as f:
    csvreader = csv.reader(f, quoting=csv.QUOTE_NONE)
    for row in csvreader:
        url = row[1].split("?")[0]
        user = row[0]
        if url not in posters_by_url:
            posters_by_url[url] = set()
        posters_by_url[url].add(user)
#print "done reading posts"

# read graph (won't do this fully normally but this allows us to compute cost easily)
# [followee] -> (ppl following them)
graph = utils.getFolloweeGraph(graph_file)

# order urls
#urls_ordered = list(posters_by_url.keys())
urls_ordered = ordering_function(posters_by_url, graph)
start_time = datetime.datetime.now()
print "done with ordering: ", start_time

# create subsets of urls seen to date
# add potential ids to the list
# [url1, url2, ...] -> [potential ids]
potential_ids_by_url = dict()
count = 0
fout = open(results_file, "w+")
fout.write("ordering\tn\tcost\treward\tnum_tuple\ttime\tavg_iding_tuple_size\n")
cost = set() # ppl we're asking 'who are someone's followers'
reward = set() # ppl de-anon'ed
tuple_sizes = []

#print "|||||||"
for url in urls_ordered:
    # just the url
    received_set = set()
    #print "posters: ", url, "----", posters_by_url[url]
    for p in posters_by_url[url]:
        # sometimes there might not be any followers; does it still requires a query? Or do we know by the degree?
        if p in graph:
            #print p, url
            cost.add(p) #TODO: cost being under-counted?
            #receivers = graph[p]
            for receiver in graph[p]:
                received_set.add(receiver)
    #print "cost: ", cost
    #print "received set size: ", len(received_set)
    potential_ids_by_url[frozenset([url])] = received_set # for just the url

    # now add url to other tuples
    count += 1
    for url_tuple in potential_ids_by_url.keys():
        # add url
        new_tuple = set(url_tuple)
        new_tuple.add(url)
        if len(new_tuple) > k:
            continue
        receivers_combined = potential_ids_by_url[url_tuple].intersection(received_set)
        if len(receivers_combined) < len(potential_ids_by_url[url_tuple]): # this new url actually adds info
            potential_ids_by_url[frozenset(new_tuple)] = receivers_combined


    # remove the empty url tuples
    to_remove = set()
    for t in potential_ids_by_url.keys():
        if len(potential_ids_by_url[t]) == 0:
            to_remove.add(t)
    for t in to_remove:
        del potential_ids_by_url[t]
    # remove url tuples which are already de-anoned

    to_remove_ided = set() #TODO: what if someone is deanoned twice?
    for t, potential_ids in potential_ids_by_url.items():
        if len(potential_ids) == 1:
            #print "deanoned: ", t, potential_ids
            reward.add(potential_ids.pop())
            tuple_sizes.append(len(t))
            to_remove_ided.add(t)
        if len(t) == k:
            to_remove_ided.add(t) # it either works or doesn't by now
    for t in to_remove_ided:
        del potential_ids_by_url[t]

    #print count, len(cost), len(reward), url, len(posters_by_url[url])

    tdelta = datetime.datetime.now() - start_time
    if len(tuple_sizes) == 0:
        avg_tuple_size = 0
    else:
        avg_tuple_size = sum(tuple_sizes)/float(len(tuple_sizes))
    fout.write(ordering_name + "\t" + str(count) + "\t" + str(len(cost)) + "\t" + str(len(reward)) + "\t" + str(len(potential_ids_by_url)) + "\t" + str(tdelta) + "\t"+ str(avg_tuple_size) + "\n")
    fout.flush()
    #print "------"
    #print "# potentially id-ed url tuples: ", len(potential_ids_by_url)
    
    #if count % 10 == 0:
    #    print count

    #if tdelta > datetime.timedelta(minutes=2):
    #    break

fout.close()

#print "FINAL:"
#for i in potential_ids_by_url.keys():
#    print i
    #print "\t", potential_ids_by_url[i]

print "=========================================================="
exit()
print potential_ids_by_url


for i in potential_ids_by_url.keys():
    print i
    print "\t", potential_ids_by_url[i]
    #for v in potential_ids_by_url[i]:
    #    print "\t", v
