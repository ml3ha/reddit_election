import praw
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import re
from stop_words import get_stop_words

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
# stop_words: a python library that contains a list of stop words, which are common words like "the", "a", "and", "of", etc.
# pip install stop_words
#



# Create the instance of praw
r = praw.Reddit(user_agent = "reddit_election", client_id = "dMh0HkXMc5viQQ", client_secret = "wr2EpWQohcSOLsYJqgKFWuFWiVU")

# The subreddits we will be scraping from
subreddits = ['The_Donald', 'HillaryClinton', 'politics']

# The fields we're interested in
fields = ['ups', 'title', 'author', 'created', 'num_comments']

# contains the relevant fields from each subreddit (both are listed above)

# Function that gets num_posts posts from the requested subreddits using the fields given
def get_top_posts(subreddits, fields, num_posts):
    # Top 50 posts from each subreddit
    ret = []
    for subreddit in subreddits:
        s = r.subreddit(subreddit)
        sub_info = defaultdict(list)
        # get the top 50 posts
        for submission in s.top(limit=num_posts):
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
        ret.append(sub_info)
    return ret

# good OOP practice
subreddit_dicts = get_top_posts(subreddits, fields, 100)

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
    subreddit_plot = activity_month.plot(kind="bar", ax=axs[index], color = colors[index])
    subreddit_plot.grid(True)
    subreddit_plot.set_xlabel("Month")
    subreddit_plot.set_ylabel("Number of top posts")
    subreddit_plot.set_title('/r/' + subreddits[index])

# So the plots don't overlap
plt.tight_layout()

# The plot title isn't accounted for in the the tight layout
plt.subplots_adjust(top = 0.9)

# save image to current directory and close the plot
fig.savefig("img/post_months.png")
plt.close()

# Count word frequencies
# Returns: a list of dataframes of word frequencies for each item in the "dfs" parameter
def get_word_frequency(dfs):
    #stop words are common words like "I, me, this, the, a, of, to, etc."
    stop_words = get_stop_words('english')
    word_freq = []
    for df in dfs:
        # keeps track of frequencies
        frequencies = defaultdict(int)
        titles = list(df.title)
        for title in titles:
            # go through each title and count frequencies
            title = title.split()
            title_cleaned = [word.strip().lower() for word in title if word.lower() not in stop_words]
            for word in title_cleaned:
                # only get the words and remove punctuation
                regex = re.compile('[^a-zA-Z]')
                word = regex.sub("", word)
                # increment frequency of that word in the dictionary by 1
                frequencies[word] += 1
        data = {"word": list(frequencies.keys()), "frequency": list(frequencies.values())}
        df_freq = pd.DataFrame(data, columns = ["word", "frequency"])
        df_freq = df_freq.sort_values(by="frequency", ascending = False)
        word_freq.append(df_freq)
    return word_freq

word_frequencies = get_word_frequency(all_data)
print(word_frequencies)

