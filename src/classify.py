#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Proof of concept for Bayes-based classificator to determine which class given
value belong.
'''



from collections import defaultdict
from math        import log
from itertools   import imap
from sys         import stderr, exit, float_info



def double_nested_factory ():
    '''
    Dirty hack for nested_factory which is required if you want (I think you want)
    to use 'pickle' module for fast save/loading of classifier object
    '''

    return {
        'count' : 0,
        'frequency' : 0.0
    }


def nested_factory ():
    '''
    Initializes structure of classifier. Classifiers have following structure:

    {
        'CLASSNAME' : {
                          'count'     : 0,
                          'frequency' : 0.0,
                          'features'  : {
                                            'FEATURE NAME' : {
                                                                 'count'     : 0,
                                                                 'frequency' : 0.0
                                                             }
                                        }
                      }
    }
    '''

    return {
        'count'     : 0,
        'frequency' : 0.0,
        'features'  : defaultdict(double_nested_factory)
    }


def train (trainme, dataset):
    '''
    Train classifier on given dataset. After training all available data
    could be used for analyzing.
    '''

    for features, label in dataset:
        trainme[label]['count'] += 1
        for feature in features:
            trainme[label]['features'][feature]['count'] += 1

    for data in trainme.itervalues():
        data['frequency'] = data['count'] / float(len(dataset))
        for feature in data['features'].itervalues():
            feature['frequency'] = feature['count'] / float(data['count'])


def get_probability (data, features):
    '''
    Calculates logarithmed probability of given feature set.

    Logarithms are used to avoid the problems which appears with calculation of
    very small float numbers. Therefore you should use 'min' instead of 'max' in
    Bayes criteria.
    '''

    if not filter(lambda f: f not in data['features'], features):
        return -log(data['frequency']) \
            - sum( log(f['frequency']) for f in data['features'].itervalues() )
    else:
        return float_info.max



def classify (classifier, features):
    '''
    Calculates the most probable class for given feature set based on information
    available from classifier.
    '''

    return min(
        classifier.iterkeys(),
        key = lambda label: get_probability(classifier[label], features)
    )


def read_data (file_name):
    '''
    Reads data from file with given file name. After that information has to be
    presented in following format:

    iterable(items(
        iterable feature set,
        class label
    ))
    '''

    data = imap(lambda line: line.decode('utf-8').split(), open(file_name))
    return tuple((get_features(line), label) for line, label in data)


def get_features (line):
    '''
    Parse line from file into one item for feature set.
    '''

    return (line[-2] + line[-1], line[0])


if __name__ == '__main__':
    classifier = defaultdict(nested_factory)

    try:
        dataset = read_data('names.txt')
    except IOError:
        print >> stderr, 'Cannot load dataset'
        exit(1)

    train(classifier, dataset)

    print classify(classifier, get_features(u'Сергей'))
