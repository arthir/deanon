# input: urls (with posters), posters (with degree)
# returns: ordered list of urls
# -------------------------------------------------------------------------------------

import sys
import datetime
sys.path.append('/home/arthi/Documents/SocialNetworks/Deanonymization/')
import utils as utils
from random import shuffle

# for all functions
# urls is a dict: [url] -> posters
# posters is a dict: [poster] -> followers

def randomOrdering(urls, posters):
    new_order = urls.keys()
    shuffle(new_order)
    return new_order


def byNumPostersHighToLow(urls, posters):
    return sorted(urls, key=lambda k: len(urls[k]), reverse=True)


def byNumPostersLowToHigh(urls, posters):
    return sorted(urls, key=lambda k: len(urls[k]))


def getNumReceiversOfURL(urls, posters): # will be an upper bound
    num_followers = dict()
    for u in urls.keys():
        num_followers[u] = 0
        for p in urls[u]:
            if p in posters: 
                num_followers[u] += len(posters[p])
    return num_followers


def byNumFollowersHighToLow(urls, posters):
    num_followers = getNumReceiversOfURL(urls, posters)
    return sorted(num_followers, key=lambda k: num_followers[k], reverse=True)


def byNumFollowersLowToHigh(urls, posters):
    num_followers = getNumReceiversOfURL(urls, posters)
    # remove those ppl with no audience - we know they won't be useful anyways
    urls_with_audience = {k: v for k, v in num_followers.iteritems() if v > 0}
    print "# urls which are received by >= 1 person: ", len(urls_with_audience)
    print "total # urls: ", len(num_followers)
    return sorted(urls_with_audience, key=lambda k: urls_with_audience[k])


def byLeastOverlapSeededwithLargestReceivedURL(urls, posters):
    print datetime.datetime.now()
    mostReceivedURL = byNumFollowersHighToLow(urls, posters)[0]
    urls_ordered = []
    urls_ordered.append(mostReceivedURL)
    posters_considered = set(urls[mostReceivedURL])

    while len(urls_ordered) < len(urls):
        min_overlap = 10000000
        min_overlap_url = ""
        for u in urls.keys():
            if u in urls_ordered:
                continue # don't consider urls that are already there
            overlap = posters_considered.intersection(urls[u])
            if len(overlap) < min_overlap:
                min_overlap = len(overlap)
                min_overlap_url = u        
        urls_ordered.append(min_overlap_url)
        for p in urls[min_overlap_url]:
            posters_considered.add(p)
        if len(urls_ordered)% 1000 == 0:
            print len(urls_ordered)
        if len(urls_ordered) > 10000:
            break
    return urls_ordered


# we also know the degree of posters
def byLeastOverlapSeededwithSmallestReceivedURL(urls, posters):
    print datetime.datetime.now()
    leastReceivedURL = byNumFollowersLowToHigh(urls, posters)[0]
    #leastReceivedURL= "http://graphics8.nytimes.com/images/2009/12/12/arts/12ritts_CA0/articleInline.jpg"
    #num_followers = getNumReceiversOfURL(urls, posters)
    urls_ordered = []
    urls_ordered.append(leastReceivedURL)
    posters_considered = set(urls[leastReceivedURL])
    print leastReceivedURL, posters_considered
    print urls[leastReceivedURL]
    print urls['http://mobile.nytimes.com/2012/12/15/opinion/the-puritan-war-on-christmas.xml']
    print "ahh!!"
    while len(urls_ordered) < len(urls):
        min_overlap = 10000000
        min_overlap_url = ""
        for u in urls.keys():
            if u in urls_ordered:
                continue # don't consider urls that are already there
            overlap = posters_considered.intersection(urls[u])
            if len(overlap) < min_overlap:
                min_overlap = len(overlap)
                min_overlap_url = u        
        urls_ordered.append(min_overlap_url)        
        print min_overlap, min_overlap_url, len(urls[min_overlap_url]), urls[min_overlap_url]
        for p in urls[min_overlap_url]:
            #if p not in posters or len(posters[p]) == 0:
            #    continue
            posters_considered.add(p)
        if len(urls_ordered)% 1000 == 0:
            print len(urls_ordered)
        if len(urls_ordered) > 10000:
            break
    print urls['http://mobile.nytimes.com/2012/12/15/opinion/the-puritan-war-on-christmas.xml']
    return urls_ordered



# we also know the degree of posters
def byLeastOverlapWithDegreeSeededwithSmallestReceivedURL(urls, posters):
    print datetime.datetime.now()
    leastReceivedURL = byNumFollowersLowToHigh(urls, posters)[0]

    urls_ordered = []
    urls_ordered.append(leastReceivedURL)
    posters_considered = urls[leastReceivedURL]

    while len(urls_ordered) < len(urls):
        min_overlap = 10000000
        min_overlap_url = ""
        for u in urls.keys():
            if u in urls_ordered:
                continue # don't consider urls that are already there
            overlap = posters_considered.intersection(urls[u])
            overlap_size = 0
            for p in overlap:
                overlap_size += len(posters[p])
            if overlap_size < min_overlap:
                min_overlap = overlap_size
                min_overlap_url = u        
        urls_ordered.append(min_overlap_url)
        print min_overlap_url, len(urls[min_overlap_url])
        for p in urls[min_overlap_url]:
            posters_considered.add(p)
        if len(urls_ordered)% 1000 == 0:
            print len(urls_ordered)
        if len(urls_ordered) > 10:
            break
    return urls_ordered
