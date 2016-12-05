import praw
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime

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
    # get the top 50 posts
    for submission in s.top(limit=50):
        # get a list of variables from each submission. There are a lot!
        variables = vars(submission)
        for field in fields:
            if field == 'author':
                # The author field is a reddit object, so we convert it to a string
                # Sometimes the reddit user will delete their account, in which their username becomes [deleted]
                author = str(variables[field]) if variables[field] is not None else '[deleted]'
                sub_info[field].append(author)
            elif field == 'created':
                # convert timestamp to datetime
                sub_info[field].append(datetime.datetime.fromtimestamp(variables[field]))
            else:
                sub_info[field].append(variables[field])
    # print(sub_info)
    subreddit_dicts.append(sub_info)

# each df below contains the data for fields above
df_republican = pd.DataFrame.from_dict(subreddit_dicts[0])
df_democrat = pd.DataFrame.from_dict(subreddit_dicts[1])
df_bipartisan = pd.DataFrame.from_dict(subreddit_dicts[2])

all_data = [df_republican, df_democrat, df_bipartisan]
colors = ['r', 'b', 'y']

# get a bar chart of how many top posts are in each month.

# make subplots (3 rows, 1 column)
fig, axs = plt.subplots(len(all_data), 1)
fig.suptitle("Monthly distribution of top post creation dates", fontweight='bold')

for index, df in enumerate(all_data):
    # iterate through each df and plot it
    activity_month = df.created.groupby(df.created.dt.month).count()
    subreddit_plot = activity_month.plot(kind="bar", ax=axs[index], y="Number of top posts", color = colors[index])
    subreddit_plot.grid(True)
    subreddit_plot.set_xlabel("Month")
    subreddit_plot.set_ylabel("Number of top posts")
    subreddit_plot.set_title('/r/' + subreddits[index])

# So the plots don't overlap
plt.tight_layout()

# The plot title isn't accounted for in the the tight layout
plt.subplots_adjust(top = 0.9)

# save image to current directory and close the plot
fig.savefig("post_months.png")
plt.close()
