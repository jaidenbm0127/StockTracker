# Jaiden Morrison
# CSCI 236
# 3/6/21
# Program 04 - APIs and Web Scraping
# 8
# Issues trying to download images
# status of the program - Runs API very well, the web scraping I had many difficulties with and is extremely simplistic


import praw  # PRAW is the Reddit API's Python wrapper
import re  # Used to clean up Strings
import matplotlib.pyplot as plt  # Used to make bar graph
from tqdm import tqdm  # Used for loading bar


def main():
    ticker_dict = {}  # Initialization

    reddit = create_reddit_instance()  # Creating a reddit instance to authenticate

    while True:  # Making a loop so the user can go as many times as they like

        subreddit_name = str(input("What subreddit to search? Some suggestions are... wallstreetbets, stocks, investing"
                                   ", or robinhoodpennystocks: "))
        sort_by = str(input("Sort by New or Hot?: "))
        post_number = int(input("How many posts to search?: "))

        subreddit = get_subreddit_instance(reddit, subreddit_name, sort_by, post_number)  # Uses previously
        # collected data to make subreddit instance with parameters

        ticker_dict = get_comments(subreddit, ticker_dict)  # Collects all comments from all posts specified and
        # gathers necessary info

        ticker_dict = sort_tickers(ticker_dict)  # Sorts dictionary by highest to lowest value

        top_one_percent_tickers = make_top_one(ticker_dict)  # As to weed out irrelevant tickers, gets the top 1%

        save_location = input("Please enter your save path, include the name of your picture. For example... \n"
                              "/home/chrx/Pictures/tickers.png... : ")
        save_graph(top_one_percent_tickers, save_location)  # Saves and displays graph

        go_again = input("Go again? Y or N: ")
        if go_again.upper() == "Y":
            pass
        if go_again.upper() == "N":
            break


# This function simply gets the sum of all values in the dictionary, multiplies it by 1% and then compares each value
# to that new number in order to weed out unnecessary keys. Returns the dictionary
def make_top_one(ticker_dict):
    total = sum(ticker_dict.values())
    percent_cutoff = total * .01
    for value in list(ticker_dict):
        if ticker_dict[value] < percent_cutoff:
            ticker_dict.pop(value)

    return ticker_dict


# The save graph function does a few things. First, it breaks the dictionary into two seperate lists. One has the key
# names, and the other has the values. Then, it assigns the key list to the x axis and values to the y axis. Finally, it
# makes labels and then saves/displays the graph
def save_graph(ticker_dict, save_location):
    stock_list = list(ticker_dict.keys())
    stock_list = stock_list[0:9]
    amount_per_stock = list(ticker_dict.values())
    amount_per_stock = amount_per_stock[0:9]
    plt.bar(stock_list, amount_per_stock)
    plt.title('Popular Tickers Right Now')
    plt.xlabel('Ticker Name')
    plt.ylabel('Amount of mentions')
    plt.savefig(save_location)
    plt.show()


# Simple function to check if a string has numbers
def has_numbers(input_string):
    return any(char.isdigit() for char in input_string)


# A running list of exceptions. Things that fit the parameters for a stock but arent actually stocks.
def exceptions(input_string):
    if input_string == "CEO" or input_string == "DD" or input_string == "EOD" or input_string == "ARE" \
            or input_string == "FOR" or input_string == "" or input_string == " ":
        return True
    else:
        return False


# Creates a reddit instance that is necessary to use the API
def create_reddit_instance():
    reddit = praw.Reddit(
        client_id="6hJ8vQ4aV4d4gw",
        client_secret="IEUn3UcYrX8p6NPPSu9Eo_FKoI9Miw",
        user_agent="Ticker Finder 0.1 (by u/HeWhoDoubts)",
    )

    return reddit


# Creates a subreddit instance. It takes the authenticated reddit instance, subreddit name, hot/new, and the amount
# of posts. Returns the subreddit instance from PRAW.
def get_subreddit_instance(reddit_instance, subreddit_name, sort_by, post_limit):
    sort_by = sort_by.upper()
    if sort_by == "HOT":
        subreddit = reddit_instance.subreddit(subreddit_name).hot(limit=post_limit)
    elif sort_by == "NEW":
        subreddit = reddit_instance.subreddit(subreddit_name).new(limit=post_limit)
    else:
        return "Some invalid data was entered."

    return subreddit


# The main workhorse of the TickerScraper. It will be easier to analyze this one line by line
def get_comments(subreddit_instance, ticker_dictionary):  # Takes the subreddit instance and ticker dictionary
    for post in tqdm(subreddit_instance, desc="Loading..."):  # Goes through each post. tqdm is the loading bar.
        for comment in post.comments:  # In each post, loop through each comment
            try:  # Tries to split a comment into each individual word
                commentList = comment.body.split()
            except AttributeError:
                pass
            for word in commentList:  # Now that each individual word has been collected, analyze each one.
                comment_no_punctuation = re.sub(r'[^\w\s]', '', word)  # Clears word of any additional punctuation
                if ("$" in word or word.isupper()) and not has_numbers(word) and 1 < len(word) < 5:  # Program checks to
                    # see if a $ symbol (denoting a stock) is present, or if the entire word is capatilized
                    # (also denoting a stock). In addition, makes sure the word is between 2 and 4 letters.
                    f = open("../../Downloads/tickerdatabase", "r")  # Opening stock database
                    for line in f:  # Iterating through each line in database
                        line = line.strip()  # Ensuring no loose whitespaces
                        if comment_no_punctuation in line and len(comment_no_punctuation) == len(line):  # Checking for
                            # match
                            if exceptions(comment_no_punctuation):  # Runs through exceptions function for an exception.
                                pass
                            else:
                                if len(ticker_dictionary) == 0:  # Checks for empty dictionary
                                    ticker_dictionary[comment_no_punctuation] = 1
                                else:
                                    for key in list(ticker_dictionary):
                                        if str(key) == comment_no_punctuation:  # Adds key if not already present
                                            ticker_dictionary[key] += 1
                                        elif comment_no_punctuation not in ticker_dictionary.keys():  # Adds 1 to
                                            # already present key
                                            ticker_dictionary[comment_no_punctuation] = 1

    return ticker_dictionary


# Sorts the dictionary from highest to smallest value
def sort_tickers(ticker_dict):
    sorted_tickers = sorted(ticker_dict.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_tickers)


if __name__ == "__main__":
    main()
