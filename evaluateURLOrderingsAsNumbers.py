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

ordering_name = sys.argv[1]
results_file = sys.argv[2]
ordering_function = eval(sys.argv[3]) # in general, this is bad since a random user could supply arbitrary code
k = int(sys.argv[4]) # max size of tuples that we keep

url_translation = dict() # [url] -> number
url_count = 1
print "start: ",  datetime.datetime.now()

def normalize_url(url):
    url = url.split("?")[0]
    url = url.split("&")[0]
    url = url.rstrip('\\')
    return url

def read_clicks(url_count):
    # read clicks [url] -> users
    clicks_by_user = dict()
    #real_ids = dict() # [fake id] -> real id
    with open(click_file, "rb") as f:
        for line in f:
            fields = line.strip().split("\t")
            user = fields[2]
            real_user = fields[0]
            url = normalize_url(fields[1])
            if url not in url_translation:
                url_translation[url] = url_count
                url_count += 1
            if url_translation[url] not in clicks_by_user:
                clicks_by_user[url_translation[url]] = set()
            clicks_by_user[url_translation[url]].add(user)
            #if real_user == "SocialArlington":
            #    print url, url_translation[url]
            #real_ids[user] = real_user
    #print "done reading clicks"
    return [clicks_by_user,url_count]


[clicks_by_user,url_count] = read_clicks(url_count)
print "# urls clicked: ", len(clicks_by_user)

def read_posts(url_count):
    # read posts
    posters_by_url = dict() # [url] -> (posters)
    #urls = utils.getURLs(posts_file, remove_trailing = True) # [poster] -> (urls)
    with open(posts_file, "rb") as f:
        csvreader = csv.reader(f, quoting=csv.QUOTE_NONE)
        for row in csvreader:
            url = normalize_url(row[1])
            user = row[0]
            if url not in url_translation:
                url_translation[url] = url_count
                url_count += 1
            if url_translation[url] not in posters_by_url:
                posters_by_url[url_translation[url]] = set()
            posters_by_url[url_translation[url]].add(user)
    print "# total urls (received or posted):",  url_count
    return posters_by_url

posters_by_url = read_posts(url_count)

graph = utils.getFolloweeGraph(graph_file) # [followee] -> (ppl following them)

# order urls
# order all of them and remove the ones that aren't clicked
urls_ordered = ordering_function(posters_by_url, graph)
to_remove = set()
for url in urls_ordered:
    if url not in clicks_by_user:
        to_remove.add(url)
for t in to_remove:
    urls_ordered.remove(t)
print "# urls considered: ", len(urls_ordered)

prev_deanoned = set()
with open("numURLsNeededForId.NYTIMES.random_noreplace.click1.txt") as f:
    for line in f:
        fields = line.split("\t")
        if "num_ppl" in line:
            continue
        if int(fields[7]) == 1:
            prev_deanoned.add(fields[0])

def getEmptyAndDoneTuples(potential_ids_by_url, reward, tuple_sizes):
    to_remove = set()

    for t, potential_ids in potential_ids_by_url.items():

        if len(potential_ids_by_url[t]) == 0: # no possible ID
            to_remove.add(t)

        if len(potential_ids) == 1: # uniquely ID-ed
            person_ided = potential_ids.pop()
            # but did that person actually click on stuff?
            is_real_tuple = True
            for u in t:
                if person_ided not in clicks_by_user[u]:
                    is_real_tuple = False
                    break
            if is_real_tuple:
                reward.add(person_ided)            
            #print "id'ed: ", person_ided, len(reward)            
                if person_ided not in prev_deanoned:
                    print "not prev done: ", person_ided
                #if person_ided=="SocialArlington":
                #    for u in t:
                #        for key,v in url_translation.items():
                #            if u == v:
                #                print "\t", key,v
                
                tuple_sizes.append(len(t))
            to_remove.add(t) # even if it wasnt a real tuple, remove it

        if len(t) == k: 
            to_remove.add(t) # it either works or doesn't by now

    return [reward, to_remove, tuple_sizes]

def getReceivers(posters_by_url, graph, url):
    received_set = set()
    for p in posters_by_url[url]:
        # sometimes there might not be any followers; does it still requires a query? Or do we know by the degree?
        if p in graph:
            cost.add(p) #TODO: cost being under-counted? 
            for receiver in graph[p]:
                received_set.add(receiver)
    #if url == 3838 or url==6031:
    #    print url, posters_by_url[url] 
    #    print received_set
    return received_set


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

for url in urls_ordered:
    count += 1
    received_set = getReceivers(posters_by_url, graph, url)
    clicked_set = clicks_by_user[url]
    #if "SocialArlington" in received_set:
    #    print url
    # add just the url
    potential_ids_by_url[frozenset([url])] = received_set # for just the url

    # now add url to other tuples
    for url_tuple in potential_ids_by_url.keys():
        if len(url_tuple) > k-1:
            continue
        # add url
        new_tuple = set(url_tuple)
        new_tuple.add(url)
        receivers_combined = potential_ids_by_url[url_tuple].intersection(received_set)
        # and this tuple has been clicked on
        #for u in url_tuple:
        #    if u in clicks_by_user:
        #        clicked_set = clicked_set.intersection(clicks_by_user[u])
        if len(receivers_combined) < len(potential_ids_by_url[url_tuple]): # and len(clicked_set) > 0: # this new url actually adds info
            potential_ids_by_url[frozenset(new_tuple)] = receivers_combined
        

    # remove the empty url tuples
    [reward, to_remove, tuple_sizes] = getEmptyAndDoneTuples(potential_ids_by_url, reward, tuple_sizes)
    for t in to_remove:
        del potential_ids_by_url[t]

    if len(tuple_sizes) == 0:
        avg_tuple_size = 0
    else:
        avg_tuple_size = sum(tuple_sizes)/float(len(tuple_sizes))
    tdelta = datetime.datetime.now() - start_time

    fout.write(ordering_name + "\t" + str(count) + "\t" + str(len(cost)) + "\t" + str(len(reward)) + "\t" + str(len(potential_ids_by_url)) + "\t" + str(tdelta) + "\t"+ str(avg_tuple_size) + "\n")
    fout.flush()

fout.close()

print "=========================================================="
