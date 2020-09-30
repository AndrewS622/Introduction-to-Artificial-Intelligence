import os
import nltk
import numpy as np
import string
import sys

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = {}
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), encoding = "utf8") as f:
            files[filename] = f.read()
    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    # get lists of forbidden words/characters
    punc = string.punctuation
    stop = nltk.corpus.stopwords.words("english")
    words = []

    # for each word in the document
    for word in nltk.word_tokenize(document.lower()):
        # remove any words consisting of punctuation
        if all(letter not in punc for letter in word):
            # remove stop words
            if word not in stop:
                words.append(word)
    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # get all unique words across all documents
    words = list(set(sum(documents.values(), [])))
    IDF = {}
    for word in words:
        n = 0
        num_doc = len(documents)
        # for each document
        for document,text in documents.items():
            # increment counter if word is in text of document
            if word in text:
                n += 1
        # record IDF
        IDF[word] = np.log(num_doc/n)
    return IDF

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    filenames = []
    TFIDF = []
    # iterate through each file
    for file, text in files.items():
        sum = 0
        # for each word in query, add IDF * word frequency if word is present in dictionary
        for word in query:
            if word in idfs.keys():
                sum += idfs[word] * text.count(word)
        filenames.append(file)
        TFIDF.append(sum)
    # sort list of tuples containing filename and TFIDF and extract filenames
    sorted_names = [f for f,_ in sorted(zip(filenames, TFIDF), key=lambda x: x[1], reverse=True)]
    return sorted_names[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_list = []
    IDF = []
    # iterate through each sentence in the document
    for sentence, text in sentences.items():
        sum = 0
        # for each word in query, add its IDF to the sum if it is in the text and the dictionary of words
        for word in query:
            if word in idfs.keys() and word in text:
                sum += idfs[word]
        sentence_list.append(sentence)
        IDF.append(sum)
    # sort tuples of sentence identifiers and IDF sums
    sorted_names = sorted(zip(sentence_list, IDF), key=lambda x: x[1], reverse=True)

    # check to make sure IDF of each of top n elements is unique
    IDF = sorted(IDF, reverse=True)
    for i in range(n):
        if IDF.count(IDF[i]) != 1:
            # if not, sort list query term density
            sorted_names = QTD_sort(IDF, sorted_names, sentences, query)
            break
    # extract sentence identifiers and return top n
    names = [s for s, _ in sorted_names]
    return names[:n]


def QTD_sort(IDF, sorted_names, sentences, query):
    """
    This function is called if multiple sentences have the same IDF sum and calculates the query term density (QTD) of
    each sentence in the document. For sentences with overlapping IDFs, the function sorts their QTDs and rearranges
    the sorted_names list accordingly.
    """
    # for each unique IDF
    for item in list(set(IDF)):
        # if it is repeated
        if IDF.count(item) > 1:
            QTD = []
            positions = []
            i = 0
            # check each tuple in sorted_names, and if a given sentence has the IDF of interest,
            for name in sorted_names:
                if name[1] == item:
                    # record its position in the tuple
                    positions.append(i)
                    sentence = sentences[name[0]]
                    sum = 0
                    # calculate the number of words in the query which appear in the sentence
                    for word in query:
                        if word in sentence:
                            sum += 1
                    # divide by the sentence length to get the QTD
                    QTD.append(sum/len(sentence))
                i += 1
            # use np.argsort to get indices which correspond to the sorted QTD list
            sorted_QTD = list(np.argsort(QTD))
            sorted_QTD.reverse()
            sorted_cpy = sorted_names.copy()

            # for each position which has the duplicate IDF
            for i in range(len(positions)):
                # switch the entry with that indicated by the sorted QTD list
                sorted_names[positions[i]] = sorted_cpy[positions[sorted_QTD[i]]]
    return sorted_names


if __name__ == "__main__":
    main()
