##
# de-x.py -- delete all your tweets w/o API access
# Copyright 2023 Thorsten Schroeder
#
# Published under 2-Clause BSD License (https://opensource.org/license/bsd-2-clause/)
#
# Please see README.md for more information
##
#%%
import sys
import json
import requests
from datetime import datetime, timedelta, UTC

format_string = "%a %b %d %H:%M:%S +0000 %Y"
min_age_days = 14
current_time = datetime.now(UTC)

def get_tweet_ids(json_data):

    result = []
    data = json.loads(json_data)

    for d in data:
        dt = datetime.strptime(d['tweet']['created_at'], format_string).replace(tzinfo=UTC)
        age = current_time - dt
        #print("dt=%s, age=%d days" % (dt, age.days))
        if age.days >= min_age_days:
            result.append(d['tweet']['id_str'])

    return result

def parse_req_headers(request_file):

    sess = {}

    with open(request_file) as f:
        line = f.readline()
        while line:
            try:
                k,v = line.split(':', 1)
                val = v.lstrip().rstrip()
                sess[k] = val
            except:
                # ignore empty lines
                pass

            line = f.readline()

    return sess

def main(ac, av):
    global min_age_days

    if(ac != 4):
        print(f"[!] usage: {av[0]} <jsonfile> <req-headers> <min-age-in-days>")
        return

    min_age_days = int(av[3])

    f = open(av[1], encoding='UTF-8')
    raw = f.read()
    f.close()

    # skip data until first '['
    i = raw.find('[')
    ids = get_tweet_ids(raw[i:])

    session = parse_req_headers(av[2])

    for i in ids:
        delete_tweet(session, i)
        # maybe add some random sleep here to prevent future rate-limiting


def delete_tweet(session, tweet_id):

    print(f"[*] delete tweet-id {tweet_id}")
    delete_url = "https://twitter.com/i/api/graphql/VaenaVgh5q5ih7kvyVjgtg/DeleteTweet"
    data = {"variables":{"tweet_id":tweet_id,"dark_request":False},"queryId":"VaenaVgh5q5ih7kvyVjgtg"}

    # set or re-set correct content-type header
    session["content-type"] = 'application/json'
    r = requests.post(delete_url, data=json.dumps(data), headers=session)
    print(r.status_code, r.reason)
    print(r.text[:500] + '...')

    return

# detect VS Code or Jupyter environment - to allow running interactively:
if sys.argv[0].endswith('\\ipykernel_launcher.py'):
    main(4, ['de-x.py', 'tweets.json', 'auth.txt', 14])
elif __name__ == '__main__':
    main(len(sys.argv), sys.argv)

    