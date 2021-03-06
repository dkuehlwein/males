#! /usr/bin/env python
'''
Created on May 3, 2013

@author: Daniel Kuehlwein
'''

import os,argparse,sys,logging,itertools,ConfigParser
from Strategy import load_strategies
from readData import compute_features,normalize_featureDict,load_data,dump_data
from createMatrix import create_application_matrix_star
from multiprocessing import Pool,cpu_count,Manager

mainPath = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parser = argparse.ArgumentParser(description='Strategy Finder 1.2 --- May 2013.')
parser.add_argument('--Setup', default = os.path.join(mainPath,'setup.ini'),  
                   help='The ini file with the learn parameters.')

def apply_strat((strategy,notSolvedYet,KMs,regGrid,cv,cvFolds)):
    strategy.create_model(notSolvedYet,KMs,regGrid,cv,cvFolds)    
    return strategy

def greedy_startStrategies(strategies,runTime=1.0,number=10):
    logger = logging.getLogger(__file__)
    startStrats = []
    solvedInRunTime = {}
    totalTime = {}
    maxSolved = -1
    maxTotalTime = 99999999
    bestStrat = None
    solved = set([])
    maxPossibleSolved = []
    maxPossibleSolvedInRunTime = []
    for s in strategies:
        totalTime[s] = 0.0
        sSolvedInRunTime = []
        for p,t in s.solvedProblems.iteritems():
            totalTime[s] += t
            if t < runTime:
                sSolvedInRunTime.append(p)
                maxPossibleSolvedInRunTime.append(p)
            maxPossibleSolved.append(p)
        if len(sSolvedInRunTime) > maxSolved or (len(sSolvedInRunTime) == maxSolved and totalTime[s] < maxTotalTime):
            maxSolved = len(sSolvedInRunTime)
            maxTotalTime = totalTime[s]
            bestStrat = s
        solvedInRunTime[s] = sSolvedInRunTime
        #print len(sSolvedIn1s)
    startStrats.append(bestStrat)
    solved = solved.union(solvedInRunTime[bestStrat])
    for _i in range(number-1):
        maxSolved = -1
        maxTotalTime = 99999999
        bestStrat = None
        for s,sS in solvedInRunTime.iteritems():
            tmp = set(sS).difference(solved)
            if len(tmp) > maxSolved  or (len(tmp) == maxSolved and totalTime[s] < maxTotalTime):
                maxSolved = len(tmp)
                maxTotalTime = totalTime[s]
                bestStrat = s
            solvedInRunTime[s] = tmp
        #if not bestStrat in startStrats: # Should always hold
        startStrats.append(bestStrat)        
        solved = solved.union(solvedInRunTime[bestStrat])
    logger.info("Solved by chosen strategies / Max solvable in runTime / Max solvable : %s / %s / %s" % \
                (len(solved),len(set(maxPossibleSolvedInRunTime)),len(set(maxPossibleSolved))))
    notSolvedYet = set(maxPossibleSolved).difference(solved)
    notSolvedYet = sorted(notSolvedYet)
    return startStrats,solved,notSolvedYet

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])
    if not os.path.exists(args.Setup):
        print 'Cannot find Setup argument at %s' % args.Setup
        sys.exit(-1)
            
    config = ConfigParser.SafeConfigParser()
    config.optionxform = str
    config.read(args.Setup)
    kernelGrid = [float(x) for x in config.get('Learn', 'KernelGrid').split(',')]
    regGrid = [float(x) for x in config.get('Learn', 'RegularizationGrid').split(',')]

    os.environ['TPTP'] = config.get('Settings', 'TPTP') 
    
    # Set up logging 
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%d-%m %H:%M:%S',
                        filename=config.get('Settings', 'LogFile'),
                        filemode='w')
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%% %(asctime)s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logger = logging.getLogger('setup.py')

    # Create initial models
    logger.info('Creating Models.')
    # Load Strategies
    logger.info("Parsing Strategy Files.")
    tmpStrategies = load_strategies(config.get('Settings', 'ResultsDir'),config.getfloat('Learn', 'CPU Bias'))  

    logger.info("Deleting dominated strategies.")
    # Get best times
    bestTimes = {}
    for s in tmpStrategies:
        for p,t in s.solvedProblems.iteritems():
            if bestTimes.has_key(p):
                if bestTimes[p] > t:
                    bestTimes[p] = t
            else:
                bestTimes[p] = t
    bestStrats = {}
    for s in tmpStrategies:
        for p,t in s.solvedProblems.iteritems():
            bestTime = bestTimes[p]                                    
            if bestStrats.has_key(p):                    
                solvedByBest = len(bestStrats[p][0].solvedProblems)
                if t < bestTime + config.getfloat('Learn', 'Tolerance'):
                    if solvedByBest < len(s.solvedProblems):
                        bestStrats[p] = [s]
                    elif solvedByBest == len(s.solvedProblems):
                        bestStrats[p].append(s)
            elif t < bestTime + config.getfloat('Learn', 'Tolerance'):                
                bestStrats[p] = [s]
    tmp2Strategies = []
    for sList in bestStrats.values():
        for s in sList:
            tmp2Strategies.append(s)
    tmp2Strategies = set(tmp2Strategies)
    logger.info('Deleted %s strategies. %s strategies left.' % (len(tmpStrategies)-len(tmp2Strategies),len(tmp2Strategies)))        
   
    # Get start strategies
    logger.info("Getting starting strategies..")
    startStrategies,solved,notSolvedYet = greedy_startStrategies(tmp2Strategies,runTime=config.getfloat('Learn', 'StartStrategiesTime'),number=config.getint('Learn', 'StartStrategies') )
    
    # Delete all problem that were solved by startStrategies and all strategies that solve none of the leftover problems.
    logger.info("Deleting all solved problems.")
    manager = Manager()    
    strategies = manager.list([])
    for s in tmp2Strategies:
        oldSolved = s.solvedProblems
        s.solvedProblems = dict([(i,oldSolved[i]) for i in notSolvedYet if i in oldSolved])
        if len(s.solvedProblems) > 0:
            strategies.append(s)

    # Load Problem Features
    if os.path.exists(config.get('Learn', 'FeaturesFile') ) and not config.getboolean('Settings', 'Clear') :
        logger.info('Loading featureFile')
        featureDict,minVals,maxVals = load_data(config.get('Learn', 'FeaturesFile') )
    else:
        logger.info('Creating feature Dict.')
        featureDict,maxVals,minVals = compute_features(notSolvedYet,config.get('Learn', 'Features'),config.getint('Settings', 'Cores'))            
        featureDict = normalize_featureDict(featureDict,maxVals,minVals)
        dump_data((featureDict,minVals,maxVals),config.get('Learn', 'FeaturesFile') )
        logger.info('Done') 
    
    # Create joint kernel matrices
    logger.info('Creating kernel matrices.')
    pool = Pool(processes = cpu_count())
    KMs = pool.map(create_application_matrix_star, itertools.izip(itertools.repeat(notSolvedYet),\
                                                                  itertools.repeat(notSolvedYet),\
                                                                  itertools.repeat(featureDict),\
                                                                  kernelGrid))       
    pool.close()
    pool.join()  
    dump_data(KMs,config.get('Learn', 'KernelFile') )
    logger.info('Done')
    
    logger.info('Learning strategy models.')        
    pool = Pool(processes = cpu_count())
    strategies = pool.map(apply_strat,itertools.izip(strategies,\
                                                     itertools.repeat(notSolvedYet),\
                                                     itertools.repeat(KMs),\
                                                     itertools.repeat(regGrid),\
                                                     itertools.repeat(config.getboolean('Learn', 'CrossValidate')),\
                                                     itertools.repeat(config.getint('Learn', 'CrossValidationFolds'))))
    pool.close()
    pool.join()  
    dump_data((strategies,notSolvedYet,kernelGrid),config.get('Learn', 'StrategiesFile') )
    dump_data((startStrategies,config.getfloat('Learn', 'StartStrategiesTime')),config.get('Learn', 'StrategiesFile')+'startStrats' )
    logger.info('All Done.')    
                     
                     
                
                
