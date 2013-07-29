#! /usr/bin/env python
'''
Automatically searches for good parameters setting for the TPTP library problems.

Created on May 2, 2013

@author: Daniel Kuehlwein
'''

import os,logging,sys,argparse,ConfigParser
from Parameters import Parameters
from Strategy import Strategy,load_strategies
from collections import deque
from Problem import getAllProblems
from cPickle import dump,load  
from multiprocessing import Pool
from random import randrange

def run_strategy((s,p,time,atpConfig)):            
    return s.run(p,time,atpConfig)

mainPath = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parser = argparse.ArgumentParser(description='Strategy Finder 1.1 --- May 2013.')
parser.add_argument('--Setup', default = os.path.join(mainPath,'setup.ini'),  
                   help='The ini file with the search parameters.')
parser.add_argument('--ATP', default = os.path.join(mainPath,'ATP.ini'),  
                   help='The ini file with the ATP parameters.')
parser.add_argument('--Strategies', default = os.path.join(mainPath,'strategies.ini'),  
                   help='The ini file with the predefined strategies.')


if __name__ == '__main__':    
    args = parser.parse_args(sys.argv[1:])
    if not os.path.exists(args.Setup):
        print 'Cannot find Setup argument at %s' % args.Setup
        sys.exit(-1)    
    if not os.path.exists(args.ATP):
        print 'Cannot find ATP argument at %s' % args.ATP
        sys.exit(-1)
    if not os.path.exists(args.Strategies):
        print 'Cannot find Strategies argument at %s.' % args.Strategies
        sys.exit(-1)    
    
    searchConfig = ConfigParser.SafeConfigParser()
    searchConfig.optionxform = str
    searchConfig.read(args.Setup)
    atpConfig = ConfigParser.SafeConfigParser()
    atpConfig.optionxform = str
    atpConfig.read(args.ATP)
    stratConfig = ConfigParser.SafeConfigParser()
    stratConfig.optionxform = str
    stratConfig.read(args.Strategies)
    
    # Set up logging 
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%d-%m %H:%M:%S',
                        filename=searchConfig.get('Settings', 'LogFile'),
                        filemode='w')
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%% %(asctime)s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logger = logging.getLogger(__file__)
    
    
    if not os.path.isdir(searchConfig.get('Settings', 'ResultsDir')):
        os.mkdir(searchConfig.get('Settings', 'ResultsDir'))
    os.environ['TPTP'] = searchConfig.get('Settings', 'TPTP')
    os.environ['TMPDIR'] = searchConfig.get('Settings', 'TmpDir')    

    logger.info('Initializing')
    if searchConfig.getboolean('Search', 'TryWithNewDefaultTime'):
        logger.info('Trying with a new default time.')
        # Load all strategies
        oldStrategies = load_strategies(searchConfig.get('Settings', 'TmpResultsDir'))

        # Load old data. 
        IS = open(searchConfig.get('Settings', 'TmpResultsPickle') ,'r')        
        _strategiesQueue,problems,Parameters,solvedProblems,_triedStrategies = load(IS)
        IS.close()
        # Find bestStrategies and only use them.
        bestStrategies = []
        for problem in problems:
            bestStrategy = None       
            bestTime = searchConfig.get('Search', 'Time')
            solvedByBest = -1
            for strat in oldStrategies:
                if strat.solvedProblems.has_key(problem.location):
                    if (strat.solvedProblems[problem.location] < bestTime) or (strat.solvedProblems[problem.location] == bestTime and len(strat.solvedProblems) > solvedByBest):
                        bestStrategy = strat
                        bestTime = strat.solvedProblems[problem.location]
                        solvedByBest = len(strat.solvedProblems)            
            # If the problem is solved, append bestStrategy
            if solvedByBest > 0:
                bestStrategies.append(bestStrategy)
        bestStrategies = set(bestStrategies)        
        # Reset strategies, only use the best strategies
        triedStrategies = set([])
        # Reset queue
        strategiesQueue = deque()
        for strat in bestStrategies:
            strategiesQueue.appendleft(strat)
        logger.info('Deleted %s strategies' % (len(oldStrategies)-len(bestStrategies)))
    elif os.path.exists(searchConfig.get('Settings', 'ResultsPickle')) and not searchConfig.getboolean('Settings', 'Clear'):
        logger.info('Loading resultsFile and continuing')
        IS = open(searchConfig.get('Settings', 'ResultsPickle'),'r')        
        strategiesQueue,problems,Parameters,solvedProblems,triedStrategies = load(IS)
        IS.close()
    else:        
        triedStrategies = set([])
        Parameters = Parameters(atpConfig)
        solvedProblems = set([])
        # Define problems
        # TODO: DEBUG ONLY
        #problems = getAllProblems(searchConfig.get('Search', 'Problems'))[-3:]
        problems = getAllProblems(searchConfig.get('Search', 'Problems'))
        
        # Load Strategies
        strategiesQueue = deque()        
        for strat in stratConfig.sections():
            newStrategy = Strategy(strat,stratConfig.items(strat))  
            strategiesQueue.append(newStrategy)
            Parameters.add_strategy(newStrategy)        
    logger.info('Initialization Complete')
     
    ATPTime = searchConfig.getint('Search','Time')   
    fullTime = searchConfig.getboolean('Search','FullTime')
    stratCounter = 0
    while not len(strategiesQueue) == 0:
        currentStrategy = strategiesQueue.popleft()
        stratCounter += 1        
        if currentStrategy.to_string() in triedStrategies:
            logger.info('Strategy in queue, but already tried: %s' % currentStrategy.name)
            continue
        solvedProblemsByCurrentStrategy = 0
        if fullTime:
            currentStrategy.runForFullTime = True
        currentStrategy.save(os.path.join(searchConfig.get('Settings', 'ResultsDir'),currentStrategy.name))
        OS = open(os.path.join(searchConfig.get('Settings', 'ResultsDir'),currentStrategy.name+'.results'),'w')
        logger.info('Trying Strategy %s. %s strategies left in queue.' % (currentStrategy.name,len(strategiesQueue)))        
        logger.debug('Problem \t Proof Found \t Time Needed \t Best Time so far')   
        triedStrategies = triedStrategies.union([currentStrategy.to_string()])        
        # Apply Strategy on all problems.
        pool = Pool(processes = searchConfig.getint('Settings', 'Cores'))
        results = pool.map_async(run_strategy,[(currentStrategy,p,ATPTime,atpConfig) for p in problems])
        pool.close()
        pool.join()
        for problem,(proofFound,timeNeeded) in zip(problems,results.get()):           
            problem.addStrategy(currentStrategy,timeNeeded)
            # If proof found, update everything.
            oldBestTime = problem.bestTime
            oldBestStrategy = problem.bestStrategy
            # Write to File            
            logger.debug('%s \t %s \t %s \t %s' % (problem.location,proofFound,timeNeeded,oldBestTime))
            if not proofFound:
                continue
            solvedProblemsByCurrentStrategy += 1
            OS.write('%s \t %s\n' % (problem.location,timeNeeded))
            if timeNeeded < problem.bestTime or problem.bestTime == None:
                problem.bestTime = timeNeeded
                problem.bestStrategy = currentStrategy
                problem.bestStrategyName = currentStrategy.name
            solvedProblems = solvedProblems.union([problem.location])
                        
            # If the strategy is good, do local search.
            if (timeNeeded < problem.bestTime) or (timeNeeded <= int(problem.bestTime)+1.0 and problem.bestTime > 0.5) or (problem.bestStrategy == currentStrategy):
                logger.debug('Good strategy found. Starting random local search.')
                logger.debug('Best Time \t Time needed \t Problem \t Strategy Name')         
                # Create random Strategies
                defaultWalkLength = searchConfig.getint('Search','WalkLength')
                walkLength = randrange(1,defaultWalkLength+1)
                randomStrategies = [Parameters.perturb(currentStrategy,walkLength) for _i in range(searchConfig.getint('Search','Walks'))] 
                for rS in randomStrategies:
                    rS.runForFullTime = False
                assert not randomStrategies[0].runForFullTime                        
                pool = Pool(processes = searchConfig.getint('Settings', 'Cores'))                
                resultsLS = pool.map_async(run_strategy,[(randomStrategy,problem,ATPTime,atpConfig) for randomStrategy in randomStrategies])
                pool.close()
                pool.join()                         
                for randomStrategy,(proofFoundLS,timeNeededLS) in zip(randomStrategies,resultsLS.get()):
                    assert not randomStrategy.name == None
                    problem.addStrategy(randomStrategy,timeNeededLS)
                    logger.debug('%s \t %s \t %s \t %s' % (problem.bestTime,timeNeededLS,problem.location,randomStrategy.name))
                    if not proofFoundLS:
                        continue                    
                    if timeNeededLS < problem.bestTime:
                        problem.bestTime = timeNeededLS
                        problem.bestStrategy = randomStrategy
                        problem.bestStrategyName = randomStrategy.name
                logger.debug('Local search finished.')
            # If the random strategy is better, add it to the Queue.            
            if oldBestTime == None or (problem.bestTime < oldBestTime and (not problem.bestStrategy in triedStrategies) and (not problem.bestStrategy == oldBestStrategy)):
                if not problem.bestStrategy.to_string() in triedStrategies: 
                    strategiesQueue.append(problem.bestStrategy)
                logger.info('New best Strategy for %s: %s' % (problem.location,problem.bestStrategyName))
            
        OS.close()

        # Store intermediate results.
        if stratCounter % 50 == 0 or fullTime or len(strategiesQueue) == 0:
            logger.debug('Dumping results')
            OS = open(searchConfig.get('Settings', 'ResultsPickle'),'w')
            dump((strategiesQueue,problems,Parameters,solvedProblems,triedStrategies),OS)
            OS.close()
            logger.debug('Done')
        if fullTime:
            logger.info('Strategy Problems Solved in DefaultTime / Total Problem Solved / Total Problems: %s / %s / %s' % (solvedProblemsByCurrentStrategy,len(solvedProblems),len(problems)))
        else:
            logger.info('Strategy Problems Solved in almost Best Time / Total Problem Solved / Total Problems: %s / %s / %s' % (solvedProblemsByCurrentStrategy,len(solvedProblems),len(problems)))
        logger.info('-----------------------------------------------------------------------------------------------')
    logger.info('Local search finished.') 
               
                    
                    
                    
                    