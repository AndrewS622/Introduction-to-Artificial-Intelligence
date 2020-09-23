import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []

    # iterate through csv file
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        # first row is headers
        header = next(reader)
        # lists of format requirements
        integers = ['Administrative', 'Informational', 'ProductRelated',
                   'OperatingSystems', 'Browser', 'Region', 'TrafficType']
        floats = ['Administrative_Duration', 'Informational_Duration',
                  'ProductRelated_Duration', 'BounceRates', 'ExitRates',
                  'PageValues', 'SpecialDay']
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'Jul', 'Aug',
                  'Sep', 'Oct', 'Nov', 'Dec']
        # for each row
        for row in reader:
            # take all columns but label
            ev = row[:-1]
            ev_mod = []
            # make current entry conform to format based on its column name and the above lists
            for i in range(len(ev)):
                item = ev[i]
                if header[i] in integers:
                    ev_mod.append(int(item))
                elif header[i] in floats:
                    ev_mod.append(float(item))
                elif header[i] == 'VisitorType':
                    ev_mod.append(1 if item == 'Returning_Visitor' else 0)
                elif header[i] == 'Weekend':
                    ev_mod.append(1 if item == 'TRUE' else 0)
                else:
                    ev_mod.append(months.index(item))
            # append modified evidence and labels
            evidence.append(ev_mod)
            labels.append(1 if row[-1] == 'TRUE' else 0)
    return (evidence, labels)

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    # train KNN with n_neighbors = 1
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    # true and false positives and negatives
    TP = 0
    TN = 0
    FN = 0
    FP = 0
    # iterate through each label-prediction combination and increment correct counter
    for label, prediction in zip(labels, predictions):
        if label == 1:
            if prediction == 1:
                TP += 1
            else:
                FN += 1
        else:
            if prediction == 0:
                TN += 1
            else:
                FP += 1
    # calculate fit parameters
    sensitivity = TP / (TP + FN)
    specificity = TN / (TN + FP)
    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
