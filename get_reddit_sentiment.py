import praw
import xlwt
import numpy as np
import pickle
from train_sentiment import clean_comment, find_features


class Tickers:
    tickers = ['mu', 'roku', ['amzn', 'amazon'], ['msft', 'microsoft'], 'amd', ['facebook',
                                                                                'fb'], ['twitter',
                                                                                        'twtr'],
               ['tsla', 'tesla'], ['spy', 'spx'], ['goog', 'google'], ['v', 'visa'], 'bac', 'ba',
               'boeing', 'pep', 'abde', 'atvi', 's&p', 'brk.b', 'brk', 'jpm', 'micron', ['nvda', 'nvidia'],
               ['snap', 'snapchat'], ['nflx', 'netflix'],
               'sq', ['chegg', 'chgg'], ['paypal', 'pypl'], 'walmart', 'ge', 'gm', 'f', 'crsp', 'baba', 'cost', 'costa',
               'square', ['ge', 'general electric'], 'ibm', ['aapl', 'apple'], ['disney', 'dis']]


def get_sentiment_score(comment, features, classifier):
    """
    Get the sentiment score for a comment. 1 = buy, 0 = sell
    :param comment: The comment to be analysed
    :param features: The set of features we're using to get the score
    :param classifier: The classifier being used to output the score
    :return:
    """
    cleaned_comment = clean_comment(comment=comment, remove_stopwords=False)
    # A list of whether each word in the comment is a feature or not
    comment_features = [find_features(comment=cleaned_comment, features=features)]
    sentiment_score = classifier.classify_many(comment_features)

    return sentiment_score


def get_past_week_comments(subreddit):
    # Setup reddit client
    reddit = praw.Reddit()

    # A list of comments which include a ticker in them
    comments_list = []

    # Get all submissions for the past week
    submissions = reddit.subreddit(subreddit).top(time_filter='week')

    for submission in submissions:
        # Allows you to see more than just the first page of comments
        submission.comments.replace_more()

        for comment in submission.comments.list():
            # Lowercase version of the comment
            comment_body = comment.body.lower()

            comments_list.append(comment_body)

    return comments_list


def get_average_sentiment(tickers):
    with open('classifier.pkl', 'rb') as f:
        with open('features.pkl', 'rb') as g:
            if isinstance(tickers, list):
                # Always use lowercase version since that's how we've trained all the models
                for index, ticker in enumerate(tickers):
                    assert isinstance(ticker, str)
                    tickers[index] = ticker.lower()
            else:
                tickers = tickers.lower()
            # The list of features for which the classifier was trained on
            features = pickle.load(g)
            # We don't want companies as features because their perception might skew the categorisation
            for ticker in Tickers.tickers:
                if ticker in features:
                    features.remove(ticker)
                    print(ticker)

            # The classifier being used to get the sentiment score
            classifier = pickle.load(f)
            # Saves the scores for the ticker so that we can take an average later
            sentiment_score_list = []
            # The subreddits we will look for comments in
            possible_subreddits = ['wallstreetbets', 'options', 'securityanalysis', 'investing', 'stocks']
            comment_list = []
            for subreddit in possible_subreddits:
                comment_list += get_past_week_comments(subreddit=subreddit)

            # Excel workbook setup
            book = xlwt.Workbook()
            sh = book.add_sheet(sheetname='Sheet_1')
            row_num = 0
            print('length of comments: {}'.format(len(comment_list)))
            for comment in comment_list:
                comment_set = set(comment.lower().split())

                tickers = tickers if isinstance(tickers, list) else [tickers]

                for ticker in tickers:
                    # Check if comment mentions the ticker
                    if ticker in comment_set:
                        sentiment_score = get_sentiment_score(comment=comment, features=features, classifier=classifier)
                        sentiment_score_list.append(sentiment_score)
                        # Write the comment to an excel file
                        sh.write(row_num, 0, comment)
                        # Write the sentiment score
                        sh.write(row_num, 1, float(sentiment_score[0]))
                        row_num += 1
                        break

            mean_score = np.mean(sentiment_score_list)

            # Give the mean score at the bottom of the sheet
            sh.write(row_num, 0, 'Mean score:')
            sh.write(row_num, 1, float(mean_score))

            # If there is actually a mean score found
            if mean_score:
                if tickers:
                    # IF it's a list use whatever the first abbreviation is
                    if isinstance(tickers, list):
                        book.save('reddit_sentiment_for_{}.xls'.format(tickers[0]))
                    else:
                        # Else just use the ticker since that's all we have
                        book.save('reddit_sentiment_for_{}.xls'.format(tickers))
                else:
                    book.save('reddit_sentiment_for_all.xls')

                return mean_score
            else:
                print('no comments found')


def main():
    for ticker in Tickers.tickers:
        ticker_sentiment = get_average_sentiment(tickers=ticker)
        print(ticker_sentiment)


if __name__ == "__main__":
    main()
