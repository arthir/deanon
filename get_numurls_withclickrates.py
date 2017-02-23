#title          : 
#description    :
#author         :Arthi Ramachandran
#date           :20140510
#version        :1      
#usage          :
#notes          :       
#python_version :2.7
#============================================================================
import sys

import datetime
import random
import numpy
import math
import csv

sys.path.append('/home/arthi/Documents/SocialNetworks/Deanonymization/')
sys.path.append('/home/arthi/Documents/SocialNetworks/Deanonymization/random_graphs')
import run_num_ppl_for_id_analysis as id_analysis
import utils as utils


def getURLs(posts_file): # returns dict of [user] => url
    print "Reading URLs"
    print  datetime.datetime.now()
    urls = dict()
    count = 0
    with open(posts_file, "rb") as f:
        csvreader = csv.reader(f, quoting=csv.QUOTE_NONE)
        for row in csvreader:
            url = row[1].split("?")[0]
            user = row[0]
            if user not in urls:
                urls[user] = set()
            urls[user].add(url)
            count += 1
            if count % 100000 == 0:
                print count
    print "done reading urls"
    return urls

def getPplPostingURLs(posts_file): # returns dict of [url] => user
    print "Reading URLs"
    print  datetime.datetime.now()
    urls = dict()
    count = 0
    with open(posts_file, "rb") as f:
        csvreader = csv.reader(f, quoting=csv.QUOTE_NONE)
        for row in csvreader:
            url = row[1].split("?")[0]
            user = row[0]
            if url not in urls:
                urls[url] = set()
            urls[url].add(user)
            count += 1
            if count % 100000 == 0:
                print count
    print "done reading urls"
    return urls


def getPplPostingUrl(url, all_ppl, urls, ppl_posting_urls):
    ppl_sending_url = set()
    if url in ppl_posting_urls:
        ppl_sending_url = ppl_posting_urls[url]
    return ppl_sending_url

def getRandomIdentifyingURLsWithoutReplacement(person, followees_set, all_ppl, followee_graph, urls, ppl_posting_urls, urls_received):
    num_urls_received = len(urls_received)
    num_urls_clicked = len(urls_received)

    if person == "lenka_TheGleek":
        print "followees: ", followees_set
    #print "RECEIVED: ", urls_received
    potential_identities = all_ppl
    best_identifying_followees = set()
    best_identifying_urls = set()
    num_followees = len(followees_set)
    #followees_left = followees_set
    urls_left = urls_received
    while len(potential_identities) > 1 and  len(urls_left) > 0 : 
        #new_followee = random.sample(followees_left, 1)[0]
        new_url = random.sample(urls_left, 1)[0]
        #print new_url
        if new_url in ppl_posting_urls:
            new_followees = ppl_posting_urls[new_url]
        else:
            new_followees = set()
        if person == "lenka_TheGleek":
            print "ppl posting url: ", new_url, new_followees
        potential_id = list()
        for new_followee in  new_followees:
            # can be any one of the union of the followers            
            if new_followee in followee_graph: 
                for f in followee_graph[new_followee]:
                    potential_id.append(f)
            best_identifying_followees.add(new_followee)
        if person == "lenka_TheGleek":
            print "potential ids: ", len(potential_id)

        if potential_identities == None or len(potential_identities)==0:
            potential_identities = set(potential_id)
            print "should never happen"
        else:
            potential_identities = potential_identities.intersection(potential_id)
        best_identifying_urls.add(new_url)
        urls_left.remove(new_url)

    if person in potential_identities:
        correct= True
    else:
        correct= False
    return [person, num_followees, len(best_identifying_followees), num_urls_clicked, num_urls_received, len(best_identifying_urls), best_identifying_urls, len(potential_identities), correct]

def main():

    posts_file = "../../Curation/postingFilteringLawRawData.txt"
    graph_file = "../../Curation/NYTIMES_FULL_PARSED.sorted.txt"


    print "reading followee graph"
    print datetime.datetime.now()
    followee_graph = utils.getFolloweeGraph(graph_file)
    print "done reading graph"
    print datetime.datetime.now()

    all_ppl = utils.getAllPpl(followee_graph)
    urls = getURLs(posts_file)
    ppl_posting_urls = getPplPostingURLs(posts_file)

    urls_clicked = dict()
    with open("nyt_urls_clicked_ctr_0.01.txt", "rb") as f:
        for line in f:
            if "real_id" in line:
                continue
            fields = line.split("\t")
            user = fields[0]
            url = fields[1]
            if user not in urls_clicked:
                urls_clicked[user] = set()
            urls_clicked[user].add(url)
    print "# users clicking: ", len(urls_clicked)
    print urls_clicked['0000000']
    print urls_clicked["007_Debby"]
    
    for click_rate in numpy.array([0.01]):
        print "Click rate: ", click_rate
        fout = open("numURLsNeededForId.NYTIMES.random_noreplace.click"+str(int(click_rate*100))+".txt", "w+")
        fout.write("person\tnum_followees\tnum_ppl_needed\tnum_urls_clicked\tnum_urls_received\tnum_urls_needed\turls_needed\tnum_ppl_identified_as_you\tcorrect\tX\n")

        with open(graph_file, "rb") as f:
            line_num = 0
            prev_follower = "_"
            followees_set = set()

            for line in f:
                line_num += 1
                fields = line.strip().split("\t")
                follower = fields[1]
                followee = fields[0]

                if prev_follower != follower: 
                    #print "PERSON", prev_follower
                    permanent_followees_set = frozenset(followees_set)
                    if prev_follower not in urls_clicked:
                        clicked_set = set()
                    else:
                        clicked_set = urls_clicked[prev_follower]
                        #print "something", prev_follower, len(urls_clicked)
                    result = getRandomIdentifyingURLsWithoutReplacement(prev_follower, followees_set, all_ppl, followee_graph, urls, ppl_posting_urls, clicked_set)
                    for field in result:
                        fout.write(str(field) + "\t")
                    fout.write("\n")
 
                    followees_set = set() 
                prev_follower = follower
                followees_set.add(followee)

if __name__ == "__main__":
    main()
