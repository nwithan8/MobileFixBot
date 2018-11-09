#!/usr/bin/python
import praw

reddit = praw.Reddit(client_id='',
                     client_secret='',
                     user_agent='MobileFixBot (by u/grtgbln)',
                     username='MobileFixBot',
                     password='')

if not reddit.read_only:
    print("Connected and ready to go!")

commentbacklog = []
#responsebacklog = []

oldcommentsfile = open("oldcomments.txt", "r")
oldcomments = oldcommentsfile.read()
oldcommentsfile.close()
print(oldcomments)

def main():
    global oldcomments
    needsfix = False
    for newcomment in reddit.subreddit('all').stream.comments():
        if commentbacklog:
            print("Handling backlog...")
            backlog()
        needsfix, fixedsubs, ogid = check(reddit.comment(id=newcomment).body, newcomment.id)
        if needsfix:
           if str(ogid) not in oldcomments:
                print("Fixing...")
                oldcomments = oldcomments + "\n" + str(ogid)
                fix(fixedsubs, ogid)

def check(text, id):
    subs = None
    fix = False
    #print(text)
    if " R/" in text:
        print(text)
        fix = True
        subs = []
        for word in text.split():
            if word.startswith("R/"):
                subs.append("r/" + word[2:])
    return fix, subs, id

def fix(fixedsubs, ogid):
    global oldcommentsfile
    global commentbacklog
    #global responsebacklog
    comment = reddit.comment(id=ogid)
    response = ""
    for fix in fixedsubs:
        response = response + str(fix) + " "
    response = response + "\n\n^(love from r/foundthemobileuser)"
    try:
        comment.reply(response)
        updateoc(ogid)
        print("Replied: " + str(response))
    except praw.exceptions.APIException:
        commentbacklog.append([comment,response])
        print("Rate limited. Adding to backlog...")
        print("Backlog : " + str(len(commentbacklog)) + " items")
        #responsebacklog.append(response)

def backlog():
    global oldcommentsfile
    global commentbacklog
    print(commentbacklog)
    for item in commentbacklog:
        try:
            item[0].reply(item[1])
            print("Replied: " + str(item[1]))
            updateoc(str(item[0].id))
            commentbacklog.remove([item[0],item[1]])
            print("Removed from backlog.")
        except praw.exceptions.APIException:
            print("Rate limited on backlog. Waiting...")
            pass

def updateoc(text):
    oc = open("oldcomments.txt","a")
    oc.write(str(text) + "\n")
    oc.close()

while True:
#    pass
    main()
