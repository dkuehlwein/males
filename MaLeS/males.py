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
from numpy import argsort,ix_
from time import time
from argparse import ArgumentParser

# Local imports
from createMatrix import create_application_matrix
from readData import get_normalized_features,load_data
from RunATP import RunATP
from thfSine import thf_sine

malesPath = dirname(dirname(realpath(__file__)))
parser = ArgumentParser(description='MaLeS 1.2 --- May 2013.')
parser.add_argument('-t','--time',help='MaLeS will run at most this long.',type=int,default=10)
parser.add_argument('-p','--problem',help='The problem that you want to solve.',default = '../test/ALG001^5.p')
parser.add_argument('--Setup', default = os.path.join(malesPath,'setup.ini'),  
                   help='The ini file with the default parameters.')
parser.add_argument('--ATP', default = os.path.join(malesPath,'ATP.ini'),
                   help='The ini file with the ATP parameters.')

def get_run_time(preferedRunTime,maxTime,startTime,ceil=True):
    timeSpent = time()-startTime
    timeLeft = round(maxTime - timeSpent+0.5,1)
    if ceil:
        preferedRunTime = round(preferedRunTime+0.5,1)        
    if preferedRunTime <= timeLeft:
        return max(0.5,preferedRunTime)
    else:
        return max(0.5,timeLeft)

def shutdown(processDict):
    for p in processDict.itervalues():
        p.terminate()
    logging.shutdown()
        
def main(argv = sys.argv[1:]):
    args = parser.parse_args(argv)
    config = ConfigParser.SafeConfigParser()
    config.optionxform = str
    if not os.path.exists(args.Setup):
        print 'Cannot find setup.ini at %s' % args.Setup
        sys.exit(-1)
    config.read(args.Setup)
    
    atpConfig = ConfigParser.SafeConfigParser()
    atpConfig.optionxform = str
    if not os.path.exists(args.ATP):
        print 'Cannot find ATP.ini at %s' % args.ATP
        sys.exit(-1)    
    atpConfig.read(args.ATP)    

    if not os.path.exists(args.problem):
        print 'Cannot find problem file: %s' % args.problem
        sys.exit(-1)    
        
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
    if config.getboolean('Settings', 'LogToFile'):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%d-%m %H:%M:%S',
                            filename=logFile,
                            filemode='w')
        console = logging.StreamHandler(outStream)
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%% %(message)s')
        console.setFormatter(formatter)    
        logger = logging.getLogger('males - %s' % args.problem)
        logger.addHandler(console)
        logger.filename=logFile
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%% %(message)s',
                            datefmt='%d-%m %H:%M:%S')
        logger = logging.getLogger('males - %s' % args.problem)
        
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
        strategyString,timeString = strategy.get_atp_string(atpConfig,args.time)
        sP = RunATP(atpConfig.get('ATP Settings','binary'),strategyString,timeString,runTime,args.problem,maxTime=args.time)
        if config.getboolean('Run', 'PauseProver'):
            processDict[strategy.name] = sP
        proofFound,_countersat,output,_time = sP.run()
        if proofFound:                    
            logger.info('\n'+output)                
            for p in processDict.itervalues():
                p.terminate()
            logger.info("Time used: %s seconds" % (time()-beginTime))
            return 0
        elif sP.is_finished():
            runTimes[strategy.name] = 9999
            if config.getboolean('Run', 'PauseProver'):
                del processDict[strategy.name]                  

    """ Not helping
    # Try THF Sine
    if config.getboolean('Settings', 'THFSine'):        
        thfSineFile = os.path.join(malesPath,'tmp',os.path.basename(args.problem)+'.thf')
        if thf_sine(args.problem,thfSineFile):
            logger.info('Running THF Sine with auto mode for 10 seconds')
            sP = RunATP(atpConfig.get('ATP Settings','binary'),'-m mode0','-t 10',10,thfSineFile,maxTime=args.time)
            proofFound,_countersat,output,_time = sP.run()
            if proofFound:                    
                logger.info('\n'+output)                
                for p in processDict.itervalues():
                    p.terminate()
                logger.info("Time used: %s seconds" % (time()-beginTime))
                return 0
            os.remove(thfSineFile)
        else:
            logger.info('THF Sine failed.')
    #"""

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
        foundNewBestStrat = False
        sortedPredictions = list(argsort(predictions))
        for bestStratIndex in sortedPredictions:
            bestStrat = strategies[bestStratIndex]
            preferedRunTime = config.getfloat('Run', 'CPUSpeedRatio') * predictions[bestStratIndex]
            runTime= get_run_time(preferedRunTime,args.time,beginTime)
            # a) if is wasn't tried before
            if not runTimes.has_key(bestStrat.name):
                runTimes[bestStrat.name] = 0.0
                foundNewBestStrat = True
                break
            # b) if the earlier best runTime is less than the current runTime and isn't finished
            if runTimes[bestStrat.name] < runTime:
                foundNewBestStrat = True
                if config.getboolean('Run', 'PauseProver'):
                    if not processDict[bestStrat.name].is_finished():
                        preferedRunTime -= runTimes[bestStrat.name] 
                        break
                else:   
                    break             
        # If we tried all options, run auto for the rest of the time
        if not foundNewBestStrat:
            pass
        
        # Determine runtime:        
        runTimes[bestStrat.name] += runTime

        logger.info("Running %s for %s seconds" % (bestStrat.name,runTime))
        # Find Process and run it
        if processDict.has_key(bestStrat.name):
            sP = processDict[bestStrat.name]
            proofFound,_countersat,output,_time = sP.cont(runTime)        
        else:
            bestStratString,bestStratTimeString = bestStrat.get_atp_string(atpConfig,args.time)
            sP = RunATP(atpConfig.get('ATP Settings','binary'),bestStratString,bestStratTimeString,runTime,args.problem,maxTime=args.time)
            if config.getboolean('Run', 'PauseProver'):
                processDict[bestStrat.name] = sP    
            proofFound,_countersat,output,_time = sP.run()
        if proofFound:                    
            logger.info('\n' + output)                
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
        

    logger.info("SZS status Timeout")
    for p in processDict.itervalues():
        p.terminate()
    logger.info("Time used: %s seconds" % (time()-beginTime))
    if not config.get('Run', 'OutputFile') == 'None':
        outStream.close()        
    return 1   
            
if __name__ == '__main__':
    sys.exit(main())