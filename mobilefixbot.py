#!/usr/bin/python
import praw
import re

reddit = praw.Reddit(client_id='',
                     client_secret='',
                     user_agent='MobileFixBot (by u/grtgbln)',
                     username='MobileFixBot',
                     password='')

if not reddit.read_only:
    print("Connected and ready to go!")

commentbacklog = []
#responsebacklog = []

oldcommentsfile = open("/home/pi/redditbots/oldcomments.txt", "r")
oldcomments = oldcommentsfile.read()
oldcommentsfile.close()
oclist = []
#print(oldcomments)
for id in oldcomments.splitlines():
    oclist.append(id)
    print(id)

sub_regex = re.compile(r' R/')

def main():
#    global oldcomments
    global sub_regex
    needsfix = False
    if commentbacklog:
        print("Handling backlog...")
        backlog()
    for newcomment in reddit.subreddit('all').stream.comments():
#        print(newcomment.body)
        if sub_regex.findall(newcomment.body):
#            print("FOUND ONE!")
            check(newcomment)
#            if str(newcomment.id) not in oclist:
#                print("Fixing...")
#                oclist.append(newcomment.id)
#                fix(newcomment)
#            needsfix, fixedsubs, ogid = check(reddit.comment(id=newcomment).body, newcomment.id)
#            if needsfix:
#                if str(ogid) not in oldcomments:
#                    print("Fixing...")
#                    oldcomments = oldcomments + "\n" + str(ogid)
#                    fix(fixedsubs, ogid)

def check(comment):
    global oclist
    if str(comment.id) not in oclist:
        print("Fixing...")
        oclist.append(comment.id)
        fix(comment)

def fix(comment):
#    global oldcommentsfile
    global commentbacklog
    global oclist
    #global responsebacklog
    response = ""
    subs = []
    for word in comment.body.split():
        if word.startswith("R/"):
            try:
                reddit.subreddits.search_by_name(word[2:], exact=True)
                subs.append("r/" + word[2:])
            except NotFound:
                pass
            #subs.append("r/" + word[2:])
    if subs:
        for fix in subs:
            response = response + str(fix) + " "
        response = response + "\n\n^(love from r/foundthemobileuser)"
        try:
            comment.reply(response)
            updateoc()
            print("Replied: " + str(response))
        except praw.exceptions.APIException:
            commentbacklog.append([comment.id,response])
            print("Rate limited. Adding to backlog...")
            print("Backlog : " + str(len(commentbacklog)) + " items")
            #responsebacklog.append(response)

def backlog():
    global oldcommentsfile
    global commentbacklog
    global reddit
    print(commentbacklog)
    for item in commentbacklog:
        try:
            reddit.comment(id=item[0]).reply(item[1])
            print("Replied: " + str(item[1]))
            updateoc()
            commentbacklog.remove([item[0],item[1]])
            print("Removed from backlog.")
        except praw.exceptions.APIException:
            print("Rate limited on backlog. Waiting...")
            pass

def updateoc():
    global oclist
    oc = open("/home/pi/redditbots/oldcomments.txt","w")
    oc.write("")
    oc.close()
    oc = open("/home/pi/redditbots/oldcomments.txt", "a")
    for id in oclist:
        oc.write(id + "\n")
    oc.close()

while True:
#    pass
    main()
