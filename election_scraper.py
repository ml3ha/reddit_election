import praw
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import re
from stop_words import get_stop_words
from ggplot import *
import scipy
import calendar

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

# python 3 way of retrieving and saving file
# get sentiment files

fields = ['ups', 'title', 'author', 'created', 'num_comments', 'selftext']


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
print("Got data from reddit")

# each df below contains the data for fields above
df_republican = pd.DataFrame.from_dict(subreddit_dicts[0])
df_democrat = pd.DataFrame.from_dict(subreddit_dicts[1])
df_bipartisan = pd.DataFrame.from_dict(subreddit_dicts[2])

all_data = [df_republican, df_democrat, df_bipartisan]
colors = ['r', 'b', 'y']

# get a bar chart of how many top posts are in each month.

# make subplots (3 rows, 1 column)
fig, axs = plt.subplots(len(all_data), 1, figsize=(15,12))
fig.suptitle("Monthly distribution of top post creation dates", fontweight='bold')

# iterate through each df and plot it
for index, df in enumerate(all_data):
    # convert x-axis to date-time (not just numbers)
    activity_month = df.created.groupby([df.created.dt.year, df.created.dt.month.apply(lambda x: calendar.month_name[x][0:3])]).count()
    activity_month.index.names = ['Year', ' Month']
    df_activity = pd.DataFrame({"date": list(activity_month.index.values), "num": list(activity_month.values)})
    df_activity.date = df_activity.date.apply(lambda x: datetime.datetime.strptime(str(x), "(%Y, '%b')"))
    df_activity = df_activity.sort_values(by="date", ascending = True)
    df_activity.date = df_activity.date.apply(lambda x: x.strftime("%b %Y"))

    # make the plot now that the data is formatted correctly
    subreddit_plot = df_activity.plot(kind="bar", ax = axs[index], color = colors[index])
    subreddit_plot.grid(True)
    subreddit_plot.set_ylabel("Number of top posts")
    subreddit_plot.set_xlabel("Month and Year")
    subreddit_plot.set_title('/r/' + subreddits[index])
    axs[index].set_xticklabels(df_activity.date, rotation = 'horizontal')
# So the plots don't overlap
plt.tight_layout()
# The plot title isn't accounted for in the the tight layout
plt.subplots_adjust(top = 0.9)

# save image to current directory and close the plot
fig.savefig("img/post_months.png", dpi=100)
plt.close()

print("plotted monthly distribution of post creation dates")

# Count word frequencies
# Returns: a list of dataframes of word frequencies for each item in the "dfs" parameter with the field provided
# Here the field is either "title" or "selftext"
def get_word_frequency(dfs, field):
    #stop words are common words like "I, me, this, the, a, of, to, etc."
    stop_words = get_stop_words('english')
    word_freq = []
    for index, df in enumerate(dfs):
        # keeps track of frequencies
        frequencies = defaultdict(int)
        text = list(df[field])
        for t in text:
            # go through each title and count frequencies
            t = t.split()
            t_cleaned = [word.strip().lower() for word in t if word.lower() not in stop_words]
            for word in t_cleaned:
                # only get the words and remove punctuation
                word = word.strip()
                regex = re.compile('[^a-zA-Z]')
                word = regex.sub("", word)
                if word:
                    # increment frequency of that word in the dictionary by 1
                    frequencies[word] += 1
        # Make the dataframe
        data = {"word": list(frequencies.keys()), "frequency": list(frequencies.values())}
        df_freq = pd.DataFrame(data, columns = ["word", "frequency"])
        df_freq = df_freq.sort_values(by="frequency", ascending = False)
        df_freq["subreddit"] = subreddits[index]
        word_freq.append(df_freq)
    return word_freq

word_frequencies = get_word_frequency(all_data, "title")
word_frequencies_self_text = get_word_frequency(all_data, "selftext")

# Plot top 10 words used in titles for each subreddit
fig, axs = plt.subplots(len(all_data), 1, figsize = (15,10))
fig.suptitle("Top 10 words used in post titles from /r/The_Donald, /r/HillaryClinton, and /r/politics", fontweight='bold')
for index, df in enumerate(word_frequencies):
    df = df[0:10]
    frequency_plot = df.plot(kind="bar",x="word", y="frequency", ax=axs[index], color = colors[index])
    frequency_plot.set_title("/r/" + subreddits[index])
    frequency_plot.set_ylabel("Occurrences")
    axs[index].set_xticklabels(axs[index].get_xticklabels(), rotation = 'horizontal')
plt.tight_layout()
plt.subplots_adjust(top = 0.9)
fig.savefig("img/word_frequency.png", dpi = 100)
plt.close()

print("Got and plotted word frequencies")

#%%
# Victoria's code with clean-up by max
# plotting word freq

# Plot word frequency
for index, df in enumerate(word_frequencies):
    df_words = df.sort_values(by="frequency", ascending = False)
    df_selftext = word_frequencies_self_text[index].sort_values(by="frequency", ascending = False)
    g = ggplot(df_words[0:10], aes(x="word", weight = "frequency", fill = "word")) +\
        geom_bar(size=30, stat="identity") + ggtitle("Most Frequently Used Words in the /r/" + subreddits[index] + " Top 100 Posts")
    g.save("img/" + subreddits[index] + "_frequency.png")
    self_text_plot = ggplot(df_selftext[0:10], aes(x="word", weight = "frequency", fill = "word")) + \
                     geom_bar(stat = "identity", size = 30) + ggtitle("Top 10 Words Used in the r/politics Subreddit's Top 100 Posts Selftext")
    self_text_plot.save("img/" + subreddits[index] + "_frequency_selftext.png")


mergeTwoDf = word_frequencies[0][:10].merge(word_frequencies[1][:10], how = "outer")
allSubredditsMerged = mergeTwoDf.merge(word_frequencies[2][:10], how = "outer")

top_10_words = [np.array(df[0:10].word) for df in word_frequencies]
top_10_self_text = [np.array(df[0:10].word) for df in word_frequencies_self_text]

np.intersect1d(top_10_words[2], top_10_words[1])
np.intersect1d(top_10_words[0], top_10_words[1])
np.intersect1d(top_10_words[0], top_10_words[2])

# all three intersect at the word "Trump"
#%%

#%%
# Confidence interval
num_subs = [r.subreddit(sub_name).subscribers for sub_name in subreddits]

for index, df in enumerate(all_data):
    df["scaled_ups"] = df.ups / num_subs[index]
    x_bar = np.mean(df["scaled_ups"])
    std = np.std(df["scaled_ups"], ddof = 1)
    ci_range = scipy.stats.t.isf(0.025, len(df) - 1) * (std / len(df) ** 0.5)
    confidence_interval = [x_bar - ci_range, x_bar + ci_range]
    print("95% confidence interval for scaled upvotes for", subreddits[index], ":", confidence_interval)

    # confidence interval for upvote to comment ratio
    df["upvote_comment_ratio"] = df.ups / df.num_comments
    x_bar = np.mean(df["upvote_comment_ratio"])
    std = np.std(df["upvote_comment_ratio"], ddof = 1)
    ci_range = scipy.stats.t.isf(0.025, len(df) - 1) * (std / len(df) ** 0.5)
    confidence_interval = [x_bar - ci_range, x_bar + ci_range]
    print("95% confidence interval for ratio of upvotes to comments", subreddits[index], ":", confidence_interval)

# Overlap between democrats & republican ratio of upvotes vs comments

