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

ordering_function = ordering.byNumFollowersLowToHigh

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
        if url not in clicks_by_user:
            clicks_by_user[url] = set()
        clicks_by_user[url].add(user)
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

# [followee] -> (ppl following them)
graph = utils.getFolloweeGraph(graph_file)

# order urls
#urls_ordered = list(posters_by_url.keys())
num_followers_per_url = ordering.getNumReceiversOfURL(posters_by_url, graph)


fout = open("num_followers_per_url_clicked_sorted.txt", "w+")
urls_ordered = ordering_function(posters_by_url, graph)
to_remove = set()
for url in urls_ordered:
    if url not in clicks_by_user:
        to_remove.add(url)
for t in to_remove:
    urls_ordered.remove(t)
print "# urls considered: ", len(urls_ordered)

fout.write("n\turl\tnum_followers\n")
count = 0
for url in urls_ordered:
    count += 1
    fout.write(str(count) + "\t" + url + "\t" + str(num_followers_per_url[url]) + "\n")
