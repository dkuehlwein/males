'''
Contains all functions necessary to parse the data.

Created on May 3, 2013

@author: Daniel Kuehlwein
'''

import os,logging,sys,subprocess,shlex
from numpy import mat
from multiprocessing import Pool,cpu_count
from cPickle import dump,load
from TimeoutThread import processTimeout

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

def expand_filename(filename):
    logger = logging.getLogger(__file__)
    # Try input name
    if os.path.isfile(filename):
        return filename
    # Try TPTP env
    TPTP = os.getenv('TPTP', '')
    if filename.startswith('/scratch/kuehlwein'):
        filename = filename.split('/')
        filename = '/'.join(filename[-3:])    
    filename = os.path.join(TPTP,filename)
    if os.path.isfile(filename):
        return filename
    # Cannot find file
    logger.warning('Cannot find problem file %s. Aborting.' % filename)
    sys.exit(-1)        


def get_tptp_plus_leo_features(filename):
    tptpFeatures = get_TPTP_features(filename)
    leoFeatures = get_leo_features(filename)
    return tptpFeatures+leoFeatures  

def run_command(command,runTime = 10):
    args = shlex.split(command)
    p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,preexec_fn=os.setsid)    
    with processTimeout(runTime, p.pid):
        stdout, _stderr = p.communicate()        
    resultcode = p.wait()
    if resultcode < 0:
        return ''
    return stdout    

def get_leo_features(filename):
    """ Return the leo features of a tptp problem """
    logger = logging.getLogger(__file__)
    features = []
    filename = expand_filename(filename)
    path = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    command = "%s/bin/leo -a %s" % (path,filename)
    #command = "/home/daniel/Downloads/leo2/bin/leo -a %s" % filename
    lines = run_command(command)    
    foundF = False
    for line in lines.split('\n'):        
        if line.startswith('#'):
            foundF = not foundF
            continue
        if not foundF:
            continue
        line = line.split('%')
        features.append(float(line[0]))
    if (len(features)> 0):
        return features
    logger.warning('Could not compute features. Using 0-Features')
    return [0.0] * 31

def get_TPTP_features(filename):
    """ Return the TPTP features of a tptp problem """
    logger = logging.getLogger(__file__)
    features = []
    filename = expand_filename(filename)
    path = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    command = "%s/bin/TPTP_features -i %s" % (path,filename)
    #print command
    lines = run_command(command)  
    for line in lines.split('\n'):
        line = line.split()
        for word in line:
            try: 
                features.append(float(word))
            except:
                continue   
    if (len(features)> 0):
        return features
    logger.warning('Could not compute features. Try running:')
    logger.warning(command)
    sys.exit(-1)

def get_e_features(filename):
    """ Return the e features of a tptp problem """
    logger = logging.getLogger(__file__)
    features = []
    filename = expand_filename(filename)
    path = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    command = "%s/bin/classify_problem -caaaaaaaaaaaaa --tstp-in %s" % (path,filename)
    #print command
    lines = run_command(command)     
    for line in lines.split('\n'):
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

def pick_feature_function(featureStyle):
    if featureStyle == 'E':
        featureFunction = get_e_features
    elif featureStyle == 'LEO':
        featureFunction = get_leo_features   
    elif featureStyle == 'TPTP+LEO':
        featureFunction = get_tptp_plus_leo_features             
    else:
        featureFunction = get_TPTP_features    
    return featureFunction


def get_normalized_features(problemFile,featureStyle,minVals,maxVals):
    featureFunction = pick_feature_function(featureStyle)
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
    featureFunction = pick_feature_function(featureStyle)    
    pool = Pool(processes = cores)            
    results = pool.map_async(featureFunction,problemsList)       
    pool.close()
    pool.join() 
    for problem,features in zip(problemsList,results.get()):
        if not setUp:
            maxVals = list(features)
            minVals = list(features)
            setUp = True        
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


#get_leo_features('/home/daniel/TPTP/TPTP-v5.4.0/Problems/SWW/SWW478^3.p')
#print get_TPTP_features('/home/daniel/TPTP/TPTP-v5.4.0/Problems/SWW/SWW478^3.p')
#print get_e_features('/home/daniel/TPTP/TPTP-v5.4.0/Problems/SWW/SWW478^3.p')
