import praw
import xlwt

# Setup reddit client
reddit = praw.Reddit()


def check_ticker(comment_body, ticker_list):
    comment_body = set(comment_body.lower().split())
    pos_words = []
    for ticker in ticker_list:
        if ticker in comment_body:
            return True

    return False


def main():
    # List of tickers to look for.
    tickers = ['mu', 'nflx', 'msft', 'roku', 'nvda', 'snap', 'amzn', 'amazon', 'microsoft', 'amd', 'facebook',
               'fb', 'twitter', 'twtr', 'tsla', 'tesla', 'spy', 'spx', 'goog', 'google', 'v', 'visa', 'bac', 'ba',
               'boeing', 'pep', 'abde', 'atvi', 's&p', 'brk.b', 'brk', 'jpm', 'micron', 'nvidia', 'snapchat', 'netflix',
               'sq', 'chegg', 'chgg', 'paypal', 'pypl', 'walmart', 'ge', 'gm', 'f', 'crsp', 'baba', 'cost', 'costa',
               'square', 'goog', 'google', 'ge', 'general electric', 'ibm', 'aapl', 'apple', 'disney', 'dis']

    # The subreddit to get the comment data from
    subreddit = 'SecurityAnalysis'

    submissions = reddit.subreddit(subreddit).hot(limit=3000)
    # Excel workbook setup
    book = xlwt.Workbook()
    sh = book.add_sheet(sheetname='Sheet_1')
    row_num = 1

    for submission in submissions:
        submission.comments.replace_more()
        for comment in submission.comments.list():
            # Check if any of the tickers are in the comment
            if check_ticker(comment_body=comment.body, ticker_list=tickers):
                # Write the comment to an excel file
                sh.write(row_num, 0, comment.body)
                row_num += 1
                print(row_num)

    book.save('{}_comments.xls'.format(subreddit))


if __name__ == "__main__":
    main()
