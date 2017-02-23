# input: social graph, ursl posted, ctr
# output: list of urls clicks
#         format: follower \t url
# ===================================================================

# rough method: 
# read graph
# read urls posted
# for all the urls received, choose ctr% of the them

import random
import sys

sys.path.append('/home/arthi/Documents/SocialNetworks/Deanonymization/')
#sys.path.append('/home/arthi/Documents/SocialNetworks/Deanonymization/random_graphs')
import utils as utils


def get_clicked_urls(graph_file, posts_file, ctr, click_file):

    #graph_file = sys.argv[1]
    #posts_file = sys.argv[2] # ../../Curation/postingFilteringLawRawData.txt

    #print "reading followee graph"
    #print datetime.datetime.now()
    #followee_graph = utils.getFolloweeGraph(graph_file)
    #print "done reading graph"
    #print datetime.datetime.now()

    #all_ppl = utils.getAllPpl(followee_graph)
    #print "NUM PPL: ", len(all_ppl)
    urls = utils.getURLs(posts_file, remove_trailing = True)
    
    fout = open(click_file, "w+")
    fout.write("real_id\turl\tanon_id\n")
    with open(graph_file, "rb") as f:
        line_num = 0
        user_count = 0
        prev_follower = "_"
        followees_set = set()

        for line in f:
            line_num += 1
            if line_num % 1000000 == 0:
                #print "----------------------------------------"
                print "LINE NUMBER    ", line_num
            fields = line.strip().split("\t")
            follower = fields[1]
            followee = fields[0]
            if prev_follower != follower: 
                urls_received = set() # TODO: count each url once? or number of times it was received?
                for fol in followees_set:
                    if fol in urls:
                        for u in urls[fol]:
                            urls_received.add(u)
                for u in urls_received:
                    if random.random() < ctr:
                        fout.write(prev_follower + "\t" + u + "\t" + "user" + str(user_count)  +"\n")
                followees_set = set() 
                user_count += 1
            prev_follower = follower
            followees_set.add(followee)
    fout.close()


ctr = 0.01
get_clicked_urls("../../Curation/NYTIMES_FULL_PARSED.sorted.txt", "../../Curation/postingFilteringLawRawData.txt", ctr, "nyt_urls_clicked_ctr_"+str(ctr)+".txt")
