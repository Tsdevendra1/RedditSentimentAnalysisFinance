import praw
import re
import nltk
import pandas as pd
from sklearn import preprocessing
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


def clean_comment(comment_body):
    """
    Cleans a comment by removing stop words and changing to lowercase
    :param comment_body: the text of a comment
    :return: List of words in the comment after being cleaned
    """
    comment_body = comment_body.lower()
    # Turns into a list of each word
    comment_body = comment_body.split()

    return comment_body


def load_positive_words():
    """
    Loads list of positive words from csv file
    :return: list of positive words
    """

    file = open('LoughranMcDonald_Positive.csv', 'r')
    positive_words = file.readlines()
    positives = [pos.strip().lower() for pos in positive_words]

    return positives


def load_negative_words():
    """
    Loads list of negative words from csv file
    :return: list of negative words
    """

    file = open('LoughranMcDonald_Negative.csv', 'r')
    negative_words = file.readlines()
    negatives = [neg.strip().lower() for neg in negative_words]

    return negatives


def count_negative_words(comment_body, negative_words):
    """
    :param comment_body: text
    :param negative_words: List of negative words to check
    :return: Number of negative words in the text
    """
    negative_words = set(negative_words)

    negatives = [word for word in comment_body if word in negative_words]

    return len(negatives)


def count_positive_words(comment_body, positive_words):
    """
    :param comment_body: text
    :param positive_words: list of positive words to check
    :return: number of positive words in text
    """
    positive_words = set(positive_words)

    positives = [word for word in comment_body if word in positive_words]

    return len(positives)


def get_sentiment(comment_body):
    """
    :param comment_body: text
    :param negative_words: list of negative words to check
    :param positive_words: list of positive words to check
    :return: Difference between number of positive and negative words
    """

    # List of positive words
    pos_words = load_positive_words()
    pos_words += ['buy', 'bull', 'call', 'bullish', 'up', 'long']

    # List of negative words
    neg_words = load_negative_words()
    neg_words += ['sell', 'bear', 'put', 'bearish', 'down', 'short']

    return count_positive_words(comment_body=comment_body, positive_words=pos_words) - count_negative_words(
        comment_body=comment_body, negative_words=neg_words)


def chunk_comment(comment_body):
    """
    :param comment_body: A list of words in the comment
    :return: A list of the comments chunked by ticker
    """

    tagged_comment = nltk.pos_tag(comment_body)

    chunk_gram = "Chunk: {<NN>+}"
    chunk_parser = nltk.RegexpParser(chunk_gram)
    chunked_comment = list(chunk_parser.parse(tagged_comment))

    return chunked_comment


def main():
    # Setup reddit client
    reddit = praw.Reddit()
    tickers = ['mu', 'nflx', 'msft', 'roku', 'appl', 'nvda', 'snap', 'amzn', 'amazon', 'microsoft', 'amd', 'facebook',
               'fb', 'twitter', 'twtr', 'tsla', 'tesla', 'spy', 'spx', 'goog', 'google', 'v', 'visa', 'bac', 'ba',
               'boeing', 'pep', 'abde', 'atvi', 's&p', 'brk.b', 'brk', 'jpm', 'micron', 'nvidia', 'snapchat', 'netflix',
               'sq', 'chegg', 'chgg', 'paypal', 'pypl', 'walmart', 'ge', 'gm', 'f', 'crsp', 'baba', 'cost', 'costa',
               'square', 'goog', 'google', 'ge', 'general electric', 'ibm']

    # Look through stream of comments for wallstreetbets subreddit
    for comment in reddit.subreddit('wallstreetbets').stream.comments():
        # Lowercase version of the comment
        comment_body = clean_comment(comment_body=comment.body)

        # Change the comment to a set to remove all duplicates and also makes searching for keywords quicker
        comment_set = set(comment.body.lower().split())

        tickers_in_comment = list()
        # Check for a mention of a ticker in the comment
        for ticker in tickers:
            if ticker in comment_set:
                # Saves which tickers are in the comment
                tickers_in_comment.append(ticker)

        # We only use comments with one ticker in them for complexity reasons for now
        if len(tickers_in_comment) == 1:
            # Calculates the sentiment score for the comment
            sentiment_score = get_sentiment(comment_body=comment_body)


if __name__ == "__main__":
    main()
