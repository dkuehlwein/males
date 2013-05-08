#! /usr/bin/env python
'''
MaLeS 1.2 

Machine Learning of Strategies. 
Creates a schedule based on the trained data and runs the ATP with the schedule.

Created on May 5, 2013

@author: Daniel Kuehlwein
'''

# Sys imports
import sys,logging,atexit,os,ConfigParser
from os.path import realpath,dirname
from multiprocessing import cpu_count
from numpy import mat,argsort,ix_
from time import time
from argparse import ArgumentParser

# Local imports
from createMatrix import create_application_matrix
from readData import get_normalized_features,load_data
from RunATP import RunATP

malesPath = dirname(dirname(realpath(__file__)))
parser = ArgumentParser(description='E-MaLeS 1.2 --- August 2012.')
parser.add_argument('-t','--time',help='MaLeS will run at most this long.',type=int,default=10)
parser.add_argument('-p','--problem',help='The problem that you want to solve.',default='foo')
parser.add_argument('--Setup', default = '../setup.ini',  
                   help='The ini file with the default parameters.')
parser.add_argument('--ATP', default = '../Satallax/satallax.ini',  
                   help='The ini file with the ATP parameters.')

def get_run_time(preferedRunTime,maxTime,startTime,ceil=True):
    timeSpent = time()-startTime
    timeLeft = round(maxTime - timeSpent+0.05,1)
    if ceil:
        preferedRunTime = round(preferedRunTime+0.05,1)        
    #print timeSpend
    #timeAvailable = maxTime-preferedRunTime
    if preferedRunTime <= timeLeft:
        #return int(preferedRunTime)
        return max(0.1,preferedRunTime)
    else:
        #return max(0,int(timeLeft))
        return max(0.1,timeLeft)

def shutdown(processDict):
    for p in processDict.itervalues():
        p.terminate()
    logging.shutdown()
        
def main(argv = sys.argv[1:]):
    args = parser.parse_args(argv)
    config = ConfigParser.SafeConfigParser()
    config.optionxform = str
    config.read(args.Setup)
    atpConfig = ConfigParser.SafeConfigParser()
    atpConfig.optionxform = str
    atpConfig.read(args.ATP)    
        
    # Debug
    #args.problem = "/home/daniel/workspace/E-MaLeS1.1/test/compts_1__t20_compts_1.p"
    #args.problem = "/home/daniel/TPTP/MPTP2078/chainy/compts_1__t16_compts_1.p"
    #args.problem = "/home/daniel/TPTP/TPTP-v5.4.0/Problems/HWV/HWV041+1.p"
    #startStrategies = [Strategy("Auto","-xAuto -tAuto ",defaultTime=300)]
    #startTime = 5
    #args.TMPDIR = "/var/tmp/"
    #args.TPTP = "/home/daniel/TPTP/TPTP-v5.4.0"
    #maxTime = 300  
        
           
    logFile = malesPath+'/tmp/'+args.problem.split('/')[-1]+'.log'
    os.environ['TPTP'] = config.get('Settings', 'TPTP')
    os.environ['TMPDIR'] = config.get('Settings', 'TmpDir')    
    if config.get('Run', 'OutputFile') == 'None':
        outStream = sys.stdout
    else:
        outStream = open(config.get('Run', 'OutputFile'),'w')
    
    # Set up logging 
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%d-%m %H:%M:%S',
                        filename=logFile,
                        filemode='w')
    console = logging.StreamHandler(outStream)
    console.setLevel(logging.INFO)
    #console.setLevel(logging.WARNING)
    formatter = logging.Formatter('%% %(message)s')
    console.setFormatter(formatter)    
    logger = logging.getLogger('males - %s' % args.problem)
    logger.addHandler(console)
    logger.filename=logFile    
    logger.info("Trying to solve %s" % args.problem)
    
    # Time
    beginTime = time()
    
    # Load data
    startStrategies,startStratsTime,strategies,notSolvedYet,kernelGrid = load_data(config.get('Run', 'StrategiesFile'))
    featureDict,minVals,maxVals = load_data(config.get('Run', 'FeaturesFile'))    

    startStratsTime *= config.getfloat('Run', 'CPUSpeedRatio') # Account for difference in training machine speed and local machine speed

    # Run startStrategies  
    processDict = {}    
    runTimes = {}
    atexit.register(shutdown,processDict)
    
    for strategy in startStrategies:
        runTime = get_run_time(startStratsTime,args.time,beginTime,ceil=False) # Need to round to the nearest integer for E
        runTimes[strategy.name] = runTime
        logger.info("Running %s for %s seconds" % (strategy.name,runTime))
        strategyString = strategy.get_atp_string(atpConfig)
        sP = RunATP(atpConfig.get('ATP Settings','binary'),strategyString,atpConfig.get('ATP Settings','time'),runTime,args.problem,maxTime=args.time)
#        sP = RunE(args.problem,strategy.to_string(),runTime,maxTime,args.proof,config.getboolean('Run', 'PauseProver'))
        if config.getboolean('Run', 'PauseProver'):
            processDict[strategy.name] = sP
        proofFound,_countersat,output,_time = sP.run()
        if proofFound:                    
            logger.info(output)                
            for p in processDict.itervalues():
                p.terminate()
            logger.info("Time used: %s seconds" % (time()-beginTime))
            return 0
        elif sP.is_finished():
            runTimes[strategy.name] = 9999
            if config.getboolean('Run', 'PauseProver'):
                del processDict[strategy.name]                  

    # Get the features of the problem and normalize them
    featureDict[args.problem] = get_normalized_features(args.problem,config.get('Learn', 'Features'),minVals,maxVals)
    
    # Create KMs
    logger.info('Creating kernel matrices.')    
    pKMs = []
    for k in kernelGrid:
        pKMs.append(create_application_matrix([args.problem],notSolvedYet,featureDict,k))
    logger.info('Done')

    while int(args.time-(time()-beginTime)) > 0:        
        # Get predictions
        predictions = []        
        for strat in strategies:            
            # Pick correct KM
            pKM = pKMs[strat.bestKernelMatrixIndex]
            predRunTime = strat.predict(pKM)
            if predRunTime < config.getfloat('Run', 'MinRunTime'):
                predRunTime = config.getfloat('Run', 'MinRunTime')
            predictions.append(predRunTime)

        # Run the strategy with shortest predicted time
        sortedPredictions = list(argsort(predictions))
        for bestStratIndex in sortedPredictions:
            bestStrat = strategies[bestStratIndex]
            #preferedRunTime = int(config.getfloat('Run', 'CPUSpeedRatio') * predictions[bestStratIndex])+1
            preferedRunTime = config.getfloat('Run', 'CPUSpeedRatio') * predictions[bestStratIndex]
            runTime= get_run_time(preferedRunTime,args.time,beginTime)
            # a) if is wasn't tried before
            if not runTimes.has_key(bestStrat.name):
                runTimes[bestStrat.name] = 0.0
                break
            # b) if the earlier best runTime is less than the current runTime and isn't finished
            if runTimes[bestStrat.name] < runTime:
                if config.getboolean('Run', 'PauseProver'):
                    if not processDict[bestStrat.name].is_finished():
                        preferedRunTime -= runTimes[bestStrat.name] 
                        break
                else:   
                    break             
                
        # Determine runtime:        
        runTimes[bestStrat.name] += runTime

        logger.info("Running %s for %s seconds" % (bestStrat.name,runTime))
        # Find Process and run it
        if processDict.has_key(bestStrat.name):
            sP = processDict[bestStrat.name]
            proofFound,_countersat,output,_time = sP.cont(runTime)        
        else:
            bestStratString = bestStrat.get_atp_string(atpConfig)
            sP = RunATP(atpConfig.get('ATP Settings','binary'),bestStratString,atpConfig.get('ATP Settings','time'),runTime,args.problem,maxTime=args.time)
#            sP = RunE(args.problem,bestStrat.to_string(),runTime,maxTime,args.proof,config.getboolean('Run', 'PauseProver'))
            if config.getboolean('Run', 'PauseProver'):
                processDict[bestStrat.name] = sP    
            proofFound,_countersat,output,_time = sP.run()
        if proofFound:                    
            logger.info(output)                
            for p in processDict.itervalues():
                p.terminate()
            logger.info("Time used: %s seconds" % (time()-beginTime))
            return 0
        elif sP.is_finished():            
            runTimes[bestStrat.name] = 9999
            if config.getboolean('Run', 'PauseProver'):
                del processDict[bestStrat.name] 

        # Update trainData
        solvedInTime = bestStrat.get_solved_in_time(float(runTimes[bestStrat.name])/config.getfloat('Run', 'CPUSpeedRatio'))        
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
        logger.debug("Updating Models")            
        newStrategies = []
        for s in strategies:
            if not s.update_model(newNotSolvedYetWithOldIndices,oldIndexNewIndexDict):
                newStrategies.append(s)
        strategies = newStrategies
        logger.debug("Done")
        
        # Update KMs            
        allSolved = False
        if newNotSolvedYetWithOldIndices == []:
            allSolved = True
        for pKMi,pKM in enumerate(pKMs):
            if not allSolved:
                pKMs[pKMi] = pKM[ix_([0],newNotSolvedYetWithOldIndices)]
            else:
                pKMs[pKMi] = []
        

    logger.info("SZS Status Timeout")
    for p in processDict.itervalues():
        p.terminate()
    logger.info("Time used: %s seconds" % (time()-beginTime))
    if not config.get('Run', 'OutputFile') == 'None':
        outStream.close()        
    return 1   
            
if __name__ == '__main__':
    sys.exit(main())