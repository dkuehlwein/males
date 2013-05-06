'''
Created on Aug 17, 2012

@author: daniel
'''
from numpy import argsort,ix_
from readData import load_data
from Problem import getAllProblems
#from emales import get_run_time,main
from males import get_run_time,main
from multiprocessing import Pool,cpu_count

if __name__ == '__main__':
    stratFile = '../tmp/strategies.pickle'
    featureFile = '../tmp/features.pickle'
    problemFileTest = '../Satallax/data/CASC24Test'
    problemFileTrain = '../Satallax/data/CASC24Training'
    KMsFile = '../tmp/models.pickle'
    problemsTrain = getAllProblems(problemFileTrain)
    problemsTest = getAllProblems(problemFileTest)    
    theorySolved = 0
    practiceSolved = 0
    time = 300
    timeBuffer = 1.0
    solveable = 511
    
    # Load data
    startStrategies,startTime,strategies,notSolvedYet,kernelGrid = load_data(stratFile)
    featureDict,minVals,maxVals = load_data(featureFile)
    KMs = load_data(KMsFile)
    
    #"""
    # Theory
    timeLeftOrig = time
    notSolvedYetOrig = notSolvedYet    
    strategiesOrig = strategies
    theorySolved = solveable - len(notSolvedYet)
    
    # Evaluate    
    for i,p in enumerate(notSolvedYetOrig):
        notSolvedYet = list(notSolvedYetOrig)
        strategies = [s.copy() for s in strategiesOrig]
        solved = False
        timeLeft = timeLeftOrig-len(startStrategies)*startTime
        alreadyTried = {}
        #print "Problem %s" % p
        # Get KMs
        pKMs = []
        for KM in KMs:
            pKMs.append(KM[i,:])
        while not solved and timeLeft > 0:            
            # Get predictions
            predictions = []        
            for strat in strategies:            
                # Pick correct KM
                pKM = pKMs[strat.bestKernelMatrixIndex]
                predictions.append(strat.predict(pKM))            
            # Run strat with shortest prediction
            sortedPredictions = list(argsort(predictions))
            for bestStratIndex in sortedPredictions:
                bestStrat = strategies[bestStratIndex]
                #preferedRunTime = int(timeBuffer * predictions[bestStratIndex])+1
                preferedRunTime = timeBuffer * predictions[bestStratIndex]
                # a) if is wasn't tried before
                if not alreadyTried.has_key(bestStrat.name):
                    alreadyTried[bestStrat.name] = 0
                    break
                # b) if the earlier best runTime is less than the current runTime
                if alreadyTried[bestStrat.name] < preferedRunTime:
                    preferedRunTime -= alreadyTried[bestStrat.name] 
                    break
            #print len(notSolvedYet),predictions[bestStratIndex],int(predictions[bestStratIndex])+1,bestStrat.name,alreadyTried.has_key(bestStrat.name),predictions
            # Run strategy        
            if timeLeft > preferedRunTime:
                runTime = preferedRunTime                
            else:
                runTime = timeLeft
            timeLeft = timeLeft - runTime
            
            #runTime,timeLeft = get_run_time(preferedRunTime,timeLeft)
            
            if bestStrat.solvedProblems.has_key(p):
                if  runTime > bestStrat.solvedProblems[p]:
                    solved = True
                    continue
            
            alreadyTried[bestStrat.name] += runTime
            
            solvedInTime = bestStrat.get_solved_in_time(float(alreadyTried[bestStrat.name])/timeBuffer)
            
            # Update notSolvedYet
            newNotSolvedYet = []
            newNotSolvedWithOldIndices = []
            oldIndexNewIndexDict = {}
            newIndex = 0
            for index,problem in enumerate(notSolvedYet):
                # Delete all problems that should have been solved by now
                if not problem in solvedInTime:
                    newNotSolvedYet.append(problem)
                    newNotSolvedWithOldIndices.append(index)
                    oldIndexNewIndexDict[index] = newIndex
                    newIndex += 1
            #print "Time left %s ,Old unsolved %s, new unsolved %s " % (timeLeft,len(notSolvedYet),len(newNotSolvedYet))
            notSolvedYet = newNotSolvedYet 
            
            
            # Update strategies / delete the ones with no problems solved!!
            newStrategies = []
            for s in strategies:
                if not s.update_model(newNotSolvedWithOldIndices,oldIndexNewIndexDict):
                    newStrategies.append(s)
            strategies = newStrategies
            
            # Update KMs            
            for pKMi,pKM in enumerate(pKMs):
                pKMs[pKMi] = pKM[ix_([0],newNotSolvedWithOldIndices)]
            
        if solved:
            theorySolved += 1
    print 'Theory',len(notSolvedYetOrig),theorySolved,solveable
    """
    print 'starting practiceTrain'    
    args = [['-t',str(time),'-p',p.location] for p in problemsTrain]
    pool = Pool(processes = cpu_count())
    results = pool.map_async(main,args)       
    pool.close()
    pool.join()  
    results.wait()
    results =  results.get()
    print "Solved/ NotSolved / Problems " 
    print len(results)-sum(results),sum(results),len(results)

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
    """
