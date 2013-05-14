'''
Contains all functions necessary to parse the data.

Created on May 3, 2013

@author: Daniel Kuehlwein
'''

import os,logging,sys,subprocess,shlex
from numpy import mat
from multiprocessing import Pool,cpu_count
from cPickle import dump,load

def load_data(fileName):
    IS = open(fileName)
    data = load(IS)
    IS.close()
    return data

def dump_data(data,fileName):
    OS = open(fileName,'w')
    dump(data,OS)
    OS.close()
    return

def get_TPTP_features(filename):
    """ Return the TPTP features of a tptp problem """
    logger = logging.getLogger(__file__)
    features = []
    # TPTP Features
    path = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.isfile(filename):
        logger.warning('Cannot find problem file. Aborting.')
        sys.exit(-1)        
    command = "%s/bin/TPTP_features -i %s" % (path,filename)
    #print command
    args = shlex.split(command)
    p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout    
    lines = p.readlines()
    p.close()       
    for line in lines:
        line = line.split()
        for word in line:
            try: 
                features.append(float(word))
            except:
                continue   
    #print len(features)    
    if (len(features)> 0):
        return features
    logger.warning('Could not compute features. Try running:')
    logger.warning(command)
    sys.exit(-1)

def get_e_features(filename):
    """ Return the e features of a tptp problem """
    logger = logging.getLogger("readData")
    features = []
    # E Features
    path = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.isfile(filename):
        logger.warning('Cannot find problem file. Aborting.')
        sys.exit(-1)        
    command = "%s/bin/classify_problem -caaaaaaaaaaaaa --tstp-in %s" % (path,filename)
    #print command
    args = shlex.split(command)
    p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout    
    lines = p.readlines()
    p.close()       
    for line in lines:
        if not line.startswith(filename):
            continue
        line = line.split('(')[1]
        line = line.split(')')[0]
        featuresStr = line.split(',')
        for i in featuresStr:
            features.append(float(i))
        return features
    logger.warning('Could not compute features. Try running:')
    logger.warning(command)
    sys.exit(-1)

def get_normalized_features(problemFile,featureStyle,minVals,maxVals):
    if featureStyle == 'E':
        featureFunction = get_e_features
    else:
        featureFunction = get_TPTP_features    
    problemFeatures = featureFunction(problemFile)
    for i in range(len(problemFeatures)):
        if not maxVals[i] == minVals[i]:
            problemFeatures[i] = (problemFeatures[i] - minVals[i]) / (maxVals[i] - minVals[i]) 
        else:
            problemFeatures[i] = 0
    normalizedFeatures = mat(problemFeatures)
    return normalizedFeatures

def compute_features(problemsList,featureStyle,cores):
    featureDict = {}
    maxVals = []
    minVals = []
    setUp = False
    #IS = open(problemsFile,'r')
    #problems = [line.strip() for line in IS]
    if featureStyle == 'E':
        featureFunction = get_e_features
    else:
        featureFunction = get_TPTP_features
    pool = Pool(processes = cores)            
    results = pool.map_async(featureFunction,problemsList)       
    pool.close()
    pool.join() 
    for problem,features in zip(problemsList,results.get()):
        if not setUp:
            maxVals = list(features)
            minVals = list(features)
            setUp = True
        print problem, len(features),len(maxVals)
        assert len(features) == len(maxVals)
        # Max/Min Values
        for i in range(len(features)):            
            if features[i] > maxVals[i]:
                maxVals[i] = features[i]
            if  features[i] < minVals[i]:
                minVals[i] = features[i]
        # Update Dicts
        featureDict[problem] = mat(features)
    return featureDict,maxVals,minVals

def normalize_featureDict(featureDict,maxVals,minVals):
    for key in featureDict.keys():
        keyF = featureDict[key]
        for i in range(keyF.shape[1]):
            if maxVals[i] == minVals[i]:
                keyF[0,i] = 0
            else:
                keyF[0,i] = (keyF[0,i] - minVals[i]) / (maxVals[i] - minVals[i]) 
            assert keyF[0,i] <= 1
            assert keyF[0,i] >= 0
    return featureDict



