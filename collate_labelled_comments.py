from xlrd import open_workbook
import xlwt


def main():
    """
    Will scan the list of comments in the excel and check if I have labelled them and then only save the ones I have labelled
    :return:
    """
    subreddit = 'SecurityAnalysis'
    workbook = open_workbook('{}_comments.xls'.format(subreddit))
    sheet = workbook.sheet_by_index(0)

    book = xlwt.Workbook()
    sh = book.add_sheet(sheetname='Sheet_1')
    counter = 0
    for row in range(1, sheet.nrows):
        comment = sheet.cell(row, 0).value
        sell_or_buy = sheet.cell(row, 1).value

        # If it has a value save it in the excel
        if sell_or_buy == 0 or sell_or_buy == 1:
            sh.write(counter, 0, comment)
            sh.write(counter, 1, sell_or_buy)
            counter += 1

    book.save('{}_comments_cleaned.xls'.format(subreddit))


if __name__ == "__main__":
    main()
