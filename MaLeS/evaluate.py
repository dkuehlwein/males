'''
Created on Aug 17, 2012

@author: daniel
'''
import logging,sys,itertools,os,numpy
from numpy import argsort,ix_
from Problem import getAllProblems
from males import main
from multiprocessing import Pool,cpu_count,Manager
from RunATP import RunATP
from Strategy import load_strategies
from readData import compute_features,normalize_featureDict,load_data,dump_data
from learn import greedy_startStrategies
from createMatrix import create_application_matrix_star,create_application_matrix
from numpy import mat
from readData import get_tptp_plus_leo_features

def apply_strat((strategy,notSolvedYet,KMs,regGrid,cv,cvFolds)):
    strategy.create_model(notSolvedYet,KMs,regGrid,cv,cvFolds)    
    return strategy

def run_males(problem):
    #print problem
    atp = RunATP('/home/daniel/workspace/males/MaLeS/males.py',
                 '',                 
                 '-t 300',
                 300,problem,pause=False)
    proofFound,_countersat,_output,usedTime = atp.run()
    return problem,proofFound,usedTime


if __name__ == '__main__':
    stratFile = '../tmp/strategies.pickle'
    featureFile = '../tmp/features.pickle'
    problemFileTest = '../Satallax/data/CASC24TestLaptop'
    problemFileTrain = '../Satallax/data/CASC24TrainingLaptop'
    KMsFile = '../tmp/models.pickle'
    problemsTrain = getAllProblems(problemFileTrain)
    problemsTest = getAllProblems(problemFileTest)    
    time = 300
    timeBuffer = 1.0
    resultsDir = '/home/daniel/workspace/males/Leo/results'
    tolerance = 1.0
    nrOfCores = 4
    kernelGrid = [0.125,0.25,0.5,1,2,4,8,16,32,64]
    regGrid = [0.25,0.5,1,2,4,8,16,32,64]
    nrOfStartStrats = 5
    startStratsRunTime = 1.0
    
    #"""
    # Set up logging 
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%d-%m %H:%M:%S',
                        filename='evaluate.log',
                        filemode='w')
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%% %(asctime)s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logger = logging.getLogger('setup.py')
    
    logger.info("Parsing Strategy Files.")
    tmpStrategies = load_strategies(resultsDir,0.3)  

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
                if t < bestTime + tolerance:
                    if solvedByBest < len(s.solvedProblems):
                        bestStrats[p] = [s]
                    elif solvedByBest == len(s.solvedProblems):
                        bestStrats[p].append(s)
            elif t < bestTime + tolerance:                
                bestStrats[p] = [s]
    tmp2Strategies = []
    for sList in bestStrats.values():
        for s in sList:
            tmp2Strategies.append(s)
    tmp2Strategies = set(tmp2Strategies)
    logger.info('Deleted %s strategies. %s strategies left.' % (len(tmpStrategies)-len(tmp2Strategies),len(tmp2Strategies)))        

    solveableProblems = set([])
    for p,t in bestTimes.iteritems():
        if t < 300:
            solveableProblems.add(p) 
    logger.info('Solveable Problems %s / %s' % (len(solveableProblems),len(problemsTrain)))               
    
    logger.info('Creating feature Dict.')
    if os.path.exists('../tmp/evalFeatures.pickle'):
        logger.info('Loading featureFile')
        featureDict,minVals,maxVals = load_data('../tmp/evalFeatures.pickle')
    else:    
        pTLocs = [p.location for p in problemsTrain]
        featureDict,maxVals,minVals = compute_features(pTLocs,'TPTP+LEO',nrOfCores)            
        featureDict = normalize_featureDict(featureDict,maxVals,minVals)
        dump_data((featureDict,minVals,maxVals),'../tmp/evalFeatures.pickle')
    #print get_tptp_plus_leo_features('/home/daniel/TPTP/TPTP-v5.4.0/Problems/ALG/ALG256^1.p')
    #print featureDict['/home/daniel/TPTP/TPTP-v5.4.0/Problems/ALG/ALG256^1.p']
    #print maxVals
    #print minVals
    #raw_input('a')

    featureDicts = []
    labels = []
    # TPTP + LEO Features
    featureDicts.append(dict(featureDict))
    labels.append('TPTP+LEO')
    # TPTP
    d = {}
    for k,f in featureDict.iteritems():
        d[k] = f[0,:-31]
    featureDicts.append(dict(d))
    labels.append('TPTP')
    # LEO
    d = {}
    for k,f in featureDict.iteritems():
        d[k] = f[0,-31:]
    featureDicts.append(dict(d))
    labels.append('LEO')
    """
    # Test
    for i in range(70):
        d = {}
        if i == 6:
            continue
        for k,f in featureDict.iteritems():
            #print i
            #print f.shape
            #print mat(f[0,:i]).shape
            #print mat(f[0,i+1:]).shape
            if i < 6:
                p1 = numpy.append(mat(f[0,:i]),mat(f[0,i+1:6]),axis = 1) 
                a = numpy.append(p1,mat(f[0,7:]),axis=1)                
            else:
                p1 = numpy.append(mat(f[0,:6]),mat(f[0,7:i]),axis = 1)
                a = numpy.append(p1,mat(f[0,i+1:]),axis=1)
            #print a.shape
            d[k] = a
        featureDicts.append(dict(d))
        labels.append('TPTP+LEO6#'+str(i))
    #"""
    tmp2StrategiesBak = tmp2Strategies
    
    for i,featureDict in enumerate(featureDicts):
        OS = open(labels[i],'w')
        #tmp2Strategies = set([x.copy() for x in tmp2StrategiesBak])
        tmp2Strategies = set([x.copy() for x in tmp2StrategiesBak])
        #Learn
        logger.info("Getting starting strategies..")
        startStrategies,solved,notSolvedYet = greedy_startStrategies(tmp2Strategies,runTime=startStratsRunTime,number=nrOfStartStrats )
        for ps in solved:
            for startI,startS in enumerate(startStrategies):
                if ps in startS.get_solved_in_time(1.0):
                    OS.write(ps +'\t' + str(startI+startS.solvedProblems[ps])+'\n')
                    break
            
        # Delete all problem that were solved by startStrategies and all strategies that solve none of the leftover problems.
        logger.info("Deleting all solved problems.")
        manager = Manager()    
        strategies = manager.list([])
        for s in tmp2Strategies:
            oldSolved = s.solvedProblems
            s.solvedProblems = dict([(i,oldSolved[i]) for i in notSolvedYet if i in oldSolved])
            if len(s.solvedProblems) > 0:
                strategies.append(s)
        logger.info('Creating kernel matrices.')
        pool = Pool(processes = nrOfCores)
        KMs = pool.map(create_application_matrix_star, itertools.izip(itertools.repeat(notSolvedYet),\
                                                                      itertools.repeat(notSolvedYet),\
                                                                      itertools.repeat(featureDict),\
                                                                      kernelGrid))       
        pool.close()
        pool.join()  
        logger.info('Done')
        
        logger.info('Learning strategy models.')        
        pool = Pool(processes = nrOfCores)
        strategies = pool.map(apply_strat,itertools.izip(strategies,\
                                                         itertools.repeat(notSolvedYet),\
                                                         itertools.repeat(KMs),\
                                                         itertools.repeat(regGrid),\
                                                         itertools.repeat(True),\
                                                         itertools.repeat(10)))
        pool.close()
        pool.join()     
        
        # Simulate Run
        # Theory
        timeLeftOrig = time 
        notSolvedYetOrig = notSolvedYet    
        theorySolved = len(solved)
        strategiesOrig = strategies
        solvedProblems = []
        
        # Evaluate    
        for i,p in enumerate(notSolvedYetOrig):
            #logger.info('Emulating MaLeS run for %s' % p)
            notSolvedYet = list(notSolvedYetOrig)
            strategies = [s.copy() for s in strategiesOrig]
            timeLeft = timeLeftOrig-len(startStrategies)*1.0
            alreadyTried = {}
            runTimes = {}
            proofFound = False
            
            for strategy in startStrategies:
                runTime = 1.0 # Need to round to the nearest integer for E
                runTimes[strategy.name] = runTime
                proofFound = p in strategy.get_solved_in_time(runTime)
                if proofFound:
                    break

            # Create KMs
            #logger.info('Creating kernel matrices.')    
            pKMs = []
            for k in kernelGrid:
                pKMs.append(create_application_matrix([p],notSolvedYet,featureDict,k))
            #logger.info('Done')
            while int(timeLeft)> 0 and not proofFound:        
                # Get predictions
                predictions = []        
                for strat in strategies:            
                    # Pick correct KM
                    pKM = pKMs[strat.bestKernelMatrixIndex]
                    predRunTime = strat.predict(pKM)
                    if predRunTime < 0.01:
                        predRunTime = 0.01
                    predictions.append(predRunTime)
                # Run the best strategy:
                # 1) Sort by predicted time 
                decentStrats = []
                bestTime = 999999
                foundNewBestStrat = False
                sortedPredictions = list(argsort(predictions))       
                # 1) Sort by predicted time     
                for bestStratIndex in sortedPredictions:
                    bestStrat = strategies[bestStratIndex]
                    preferedRunTime = 1.0 * predictions[bestStratIndex]
                    preferedRunTime = 1.0 * predictions[bestStratIndex]
                    preferedRunTime = round(preferedRunTime+0.05,2)    
                    if preferedRunTime <= timeLeft:
                        runTime = max(0.1,preferedRunTime)
                    else:
                        runTime =  max(0.1,timeLeft)
                    if runTime > bestTime:
                        break
                    # a) if is wasn't tried before
                    if not runTimes.has_key(bestStrat.name):
                        runTimes[bestStrat.name] = 0.0
                        decentStrats.append(bestStrat)
                        bestTime = runTime
                    # b) if the earlier best runTime is less than the current runTime and isn't finished
                    elif runTimes[bestStrat.name] < runTime:
                        decentStrats.append(bestStrat)
                        bestTime = runTime
                                
                # 2) Prefer Strats that haven't been tried before
                decentStrats.sort(key = lambda s: bestTime-runTimes[s.name],reverse=True)
                runTimeX = bestTime-runTimes[decentStrats[0].name]
                newDecentStrats = [s for s in decentStrats if (bestTime-runTimes[s.name]) == runTimeX]
                # 3) Pick the start with the most solved problems
                if len(newDecentStrats) > 0:
                    newDecentStrats.sort(key = lambda s: s.get_solved_in_time(runTime),reverse=True)
                    mostSolved = len(newDecentStrats[0].get_solved_in_time(runTime))
                    #if len(newDecentStrats) > 1:
                    #    print mostSolved, len(newDecentStrats[-1].get_solved_in_time(runTime))
                    newDecentStrats = [s for s in newDecentStrats if len(s.get_solved_in_time(runTime)) == mostSolved]                
                if len(newDecentStrats) > 0 and mostSolved > 0:
                    foundNewBestStrat = True
                    bestStrat = newDecentStrats[0]
                    if len(newDecentStrats) > 1:
                        logger.warning('More than one strat choice. %s' % len(newDecentStrats))
                        #for s in newDecentStrats:
                        #    print s.name,runTime,leastSolved           
                        
                # If we tried all options, run auto for the rest of the time
                if not foundNewBestStrat:
                    #logger.info('Tried all predictions. Running global best for remaining time.')
                    bestStrat = startStrategies[0]
                    runTime = timeLeft
                    
                
                # Determine runtime:        
                runTimes[bestStrat.name] += runTime
                timeLeft = timeLeft - runTime
        
                #logger.info("Running %s for %s seconds" % (bestStrat.name,runTime))
                # Find Process and run it
                proofFound = p in bestStrat.get_solved_in_time(runTime)
        
                # Update trainData
                solvedInTime = bestStrat.get_solved_in_time(float(runTimes[bestStrat.name]))        
                newNotSolvedYet = []
                newNotSolvedYetWithOldIndices = []
                oldIndexNewIndexDict = {}
                newIndex = 0
                for index,problem in enumerate(notSolvedYet):
                    # Delete all problems that should have been solved by now
                    if not problem in solvedInTime:
                        newNotSolvedYet.append(problem)
                        newNotSolvedYetWithOldIndices.append(index)
                        oldIndexNewIndexDict[index] = newIndex
                        newIndex += 1
                notSolvedYet = newNotSolvedYet 
                
                # Update strategies / delete the ones with no problems solved!!
                #logger.debug("Updating Models")            
                newStrategies = []
                for s in strategies:
                    if not s.update_model(newNotSolvedYetWithOldIndices,oldIndexNewIndexDict):
                        newStrategies.append(s)
                strategies = newStrategies
                #logger.debug("Done")
                
                # Update KMs            
                allSolved = False
                if newNotSolvedYetWithOldIndices == []:
                    allSolved = True
                for pKMi,pKM in enumerate(pKMs):
                    if not allSolved:
                        pKMs[pKMi] = pKM[ix_([0],newNotSolvedYetWithOldIndices)]
                    else:
                        pKMs[pKMi] = []
            #x = raw_input('a')    
            
            if proofFound:
                theorySolved += 1
                solvedProblems.append(p)
                #print 'Found Proof for %s' % p
                OS.write(p +'\t'+ str(300-timeLeft)+'\n')
           
        print 'Theory eval: origNotSolved %s, theorysolved %s, solvable %s ' % (len(notSolvedYetOrig),theorySolved,len(solveableProblems))
        OS.close()
    #"""
    
    """
    # Load data
    startStrategies,startTime,strategies,notSolvedYet,kernelGrid = load_data(stratFile)
    featureDict,minVals,maxVals = load_data(featureFile)
    KMs = load_data(KMsFile)

    print 'starting practiceTrain'    
    OS = open('SatallaxResultsTrain','w')
    args = ['-p /home/daniel/TPTP/TPTP-v5.4.0/' +p.location for p in problemsTrain]
    #args = [['-t',str(time),'-p','/home/daniel/TPTP/TPTP-v5.4.0/Problems/ALG/ALG256^1.p']]
    #args = ['-p /scratch/kuehlwein/TPTP-v5.4.0/Problems/ALG/ALG256^1.p']
    pool = Pool(processes = 4)
    results = pool.map_async(run_males,args[:50])
    pool.close()
    pool.join()
    results.wait()
    results =  results.get()
    for problem,proofFound,usedTime in results:
        print problem,proofFound,usedTime
        if proofFound:
            OS.write(problem + '\t' + str(usedTime) + '\n')
    OS.close()
    #"""


    """
    print 'starting practiceTest'    
    args = [['-t',str(time),'-p',p.location] for p in problemsTest]
    pool = Pool(processes = cpu_count())
    results = pool.map_async(main,args)       
    pool.close()
    pool.join()  
    results.wait()
    results =  results.get()
    print "Solved/ NotSolved / Problems " 
    print len(results)-sum(results),sum(results),len(results)
    #"""
