import pickle
import nltk
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.corpus import stopwords
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import random
from xlrd import open_workbook


def clean_features(features):
    """
    :return: Removes any mention of the tickers because that shouldn't effect the sentiment score. Because we are trying to generalise.
    """

    tickers = ['mu', 'nflx', 'msft', 'roku', 'nvda', 'snap', 'amzn', 'amazon', 'microsoft', 'amd', 'facebook',
               'fb', 'twitter', 'twtr', 'tsla', 'tesla', 'spy', 'spx', 'goog', 'google', 'v', 'visa', 'bac', 'ba',
               'boeing', 'pep', 'abde', 'atvi', 's&p', 'brk.b', 'brk', 'jpm', 'micron', 'nvidia', 'snapchat', 'netflix',
               'sq', 'chegg', 'chgg', 'paypal', 'pypl', 'walmart', 'ge', 'gm', 'f', 'crsp', 'baba', 'cost', 'costa',
               'square', 'goog', 'google', 'ge', 'general electric', 'ibm', 'aapl', 'apple', 'disney', 'dis']

    features = set(features)

    for ticker in tickers:
        if ticker in features:
            features.remove(ticker)

    return list(features)


def get_accuracy(classifier_type, test_set):
    """
    :return: Percentage accuracy of the classifier on the test_set
    """
    return nltk.classify.accuracy(classifier_type, test_set) * 100


def classify(training_set, test_set):
    """
    runs different types of classifiers to see which performs best
    :param training_set:
    :param test_set:
    :return: best performing classifier and it's accuracy
    """
    results = {}

    naive_classifier = nltk.NaiveBayesClassifier.train(training_set)
    results[naive_classifier] = get_accuracy(classifier_type=naive_classifier, test_set=test_set)

    logistic_regression_classifier = SklearnClassifier(LogisticRegression(solver='lbfgs'))
    logistic_regression_classifier.train(training_set)
    results[logistic_regression_classifier] = get_accuracy(classifier_type=logistic_regression_classifier,
                                                           test_set=test_set)
    sgdc_classifier = SklearnClassifier(SGDClassifier(max_iter=1000, tol=1e-3))
    sgdc_classifier.train(training_set)
    results[sgdc_classifier] = get_accuracy(classifier_type=sgdc_classifier, test_set=test_set)

    nu_svc_classifier = SklearnClassifier(NuSVC(gamma='scale'))
    nu_svc_classifier.train(training_set)
    results[nu_svc_classifier] = get_accuracy(classifier_type=nu_svc_classifier, test_set=test_set)

    linear_svc_classifier = SklearnClassifier(LinearSVC())
    linear_svc_classifier.train(training_set)
    results[linear_svc_classifier] = get_accuracy(classifier_type=linear_svc_classifier, test_set=test_set)

    multinomial_nb_classifier = SklearnClassifier(MultinomialNB())
    multinomial_nb_classifier.train(training_set)
    results[multinomial_nb_classifier] = get_accuracy(classifier_type=multinomial_nb_classifier, test_set=test_set)

    random_forest_classifier = SklearnClassifier(RandomForestClassifier(n_estimators=100))
    random_forest_classifier.train(training_set)
    results[random_forest_classifier] = get_accuracy(classifier_type=random_forest_classifier, test_set=test_set)

    neural_network_classifier = SklearnClassifier(MLPClassifier(max_iter=1000))
    neural_network_classifier.train(training_set)
    results[neural_network_classifier] = get_accuracy(classifier_type=neural_network_classifier, test_set=test_set)

    current_max_accuracy = 0
    best_classifier = None
    for classifier, accuracy in results.items():
        if accuracy > current_max_accuracy:
            current_max_accuracy = accuracy
            best_classifier = classifier

    return best_classifier, current_max_accuracy


def find_features(comment, features):
    """
    :param comment: List of words in a comment
    :param features: the features we are checking for
    :return: A dictionary containing whether each word in wsb_comment is a feature or not (True/False)
    """
    words = set(comment)
    comment_features = {}
    # Keeps check if there any features at all in the comment
    has_features = 0

    for w in features:
        comment_features[w] = (w in words)
        if w in words:
            has_features += 1

    return comment_features if has_features else False


def clean_comment(comment, remove_stopwords):
    """
    :param remove_stopwords: Whether stopwords should be removed or not
    :param comment: String of the comment
    :return: A list with all words in lowercase and with stop words remove if the parameter is true
    """
    if remove_stopwords:
        # Remove unnecessary words by checking if they're in this set
        stop_words = set(stopwords.words("english"))

        # Similar to .split() but also lets punctuation act as words
        words = comment.lower().split()

        # Sentence without stop words
        filtered_sentence = [word for word in words if word not in stop_words]
    else:
        filtered_sentence = comment.lower().split()

    return filtered_sentence


def clean_all_words(min_word_freq, all_words):
    # Shows how many times each word comes up
    all_words = nltk.FreqDist(all_words)

    # Get a list of the features
    all_words = [word for word, frequency in all_words.items() if frequency > min_word_freq]

    # Removes mention of tickers
    all_words = clean_features(features=all_words)

    return all_words


def get_comment_features(features, data):
    feature_set = []

    for (comment, label) in data:
        comment_features = find_features(comment=comment, features=features)

        if comment_features:
            feature_set.append((comment_features, label))

    return feature_set


def calculate_accuracy():
    # Will contain tuples of the words in a comment as well as it's label
    data = list()
    all_words = list()

    workbook = open_workbook('comment_data/overall_comments_cleaned.xls')
    sheet = workbook.sheet_by_index(0)

    # Go through the data in the excel sheet
    for row in range(sheet.nrows):
        # Get comment value
        comment = sheet.cell(row, 0).value
        # Whether it is a buy or sell category
        sell_or_buy = sheet.cell(row, 1).value

        data.append((comment, int(sell_or_buy)))
        all_words += clean_comment(comment, remove_stopwords=False)

    # Keep it random
    random.shuffle(data)

    features = clean_all_words(min_word_freq=2, all_words=all_words)

    feature_sets = get_comment_features(features=features, data=data)

    # What percentage of the data should be used for validation (out of 1)
    validation_percentage_of_data = 0.2

    training_set_amount = round(len(feature_sets) * (1 - validation_percentage_of_data))

    training_set = feature_sets[:training_set_amount]
    test_set = feature_sets[training_set_amount:]

    return classify(training_set=training_set, test_set=test_set)


def main():
    current_max_accuracy = None
    current_max_classifier = None
    # Run 100 times to get the best accuracy classifier
    for i in range(100):
        classifier, accuracy = calculate_accuracy()
        print(accuracy)
        if current_max_accuracy is None or accuracy > current_max_accuracy:
            current_max_accuracy = accuracy
            current_max_classifier = classifier

    print(current_max_accuracy)

    save_best_classifier = False
    if save_best_classifier:
        # now you can save it to a file
        with open('classifier_2.pkl', 'wb') as f:
            pickle.dump(current_max_classifier, f)


if __name__ == "__main__":
    main()
