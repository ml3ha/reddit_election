import praw
from collections import defaultdict
from pprint import pprint
import matplotlib.pyplot as plt
import pandas as pd
# Summary of pip packages we're using:
# praw: Reddit api scraper with a collection of methods that can be used to retrieve data from reddit.com
# pip install praw
#
# defaultdict: A nice dictionary which defaults to a value if a key hasn't been set yet. A bit more convenient than a regular dictionary,
# since you would have to check if a key existed first for a regular dictionary.
#
# pprint: pretty print package which formats dictionaries and json nicely so that they are easily readable
# pip install pprint
#
# matplotlib: plotting package for data structures in python
# pip install matplotlib
#

# Create the instance of praw
r = praw.Reddit(user_agent = "reddit_election", client_id = "dMh0HkXMc5viQQ", client_secret = "wr2EpWQohcSOLsYJqgKFWuFWiVU")

# The subreddits we will be scraping from
subreddits = ['The_Donald', 'HillaryClinton', 'politics']

# The fields we're interested in
fields = ['ups', 'title', 'author', 'created', 'num_comments']

# contains the relevant fields from each subreddit (both are listed above)
subreddit_dicts = []


# Top 50 posts from each subreddit
for subreddit in subreddits:
    s = r.subreddit(subreddit)
    sub_info = defaultdict(list)
    for submission in s.top(limit=50):
        variables = vars(submission)
        for field in fields:
            if field == 'author':
                sub_info[field].append(str(variables[field]))
            else:
                sub_info[field].append(variables[field])
    # print(sub_info)
    subreddit_dicts.append(sub_info)

#pprint(subreddit_dicts)

the_donald_df = pd.DataFrame.from_dict(subreddit_dicts[0])

pprint(df)

plt.plot(subreddit_dicts[0]['ups'])
plt.show()