'''
Created on May 2, 2013

@author: Daniel Kuehlwein
'''

import copy,os,ConfigParser,numpy
import logging
from RunATP import RunATP
from CrossValidation import cross_validate

def create_leo_string(parameters):
    parameterList = []
    for param,val in sorted(parameters.items()):
        if val == False or val == 'False':
            continue
        elif param.startswith('--') and (val == True or val == 'True'):
            parameterList.append(param)
        elif param.startswith('--'):
            parameterList.append(' '.join([param,val]))
        else:
            parameterList.append(''.join([param,val]))
    return ' '.join(parameterList)


def create_E_string(parameters):
    parameterList = []
    for param,val in sorted(parameters.items()):
        if val == False or val == 'False':
            continue
        elif param.startswith('--') and (val == True or val == 'True'):
            parameterList.append(param)
        elif param.startswith('--'):
            parameterList.append('='.join([param,val]))
        else:
            parameterList.append(''.join([param,val]))
    return ' '.join(parameterList)

def create_satallax_string(binary,name,parameters,runBefore):    
    if not runBefore:
        binDir = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(binary))))    
        modesDir = os.path.join(binDir,'modes')
        modeFile = os.path.join(modesDir,name)
        if not  os.path.exists(modeFile):    
            OS = open(modeFile,'w')
            for param,val in parameters.items():
                OS.write(param+'\n')            
                OS.write(str(val).lower()+'\n')
            OS.close()
    return '-m %s' % name
    

def load_strategies(folder,bias = 0.0):
    strategies = []
    for stratFile in os.listdir(folder):
        if not stratFile.endswith('.results'):
            continue
        stratName = stratFile.split('.')[0]
        IS = open(os.path.join(folder,stratFile),'r')
        lines = IS.readlines()
        IS.close()    
        if len(lines) == 0:   
            logger = logging.getLogger(__file__)
            logger.debug('Found empty file: %s' % os.path.join(folder,stratFile))
            continue        
        strategy = load_strategy(os.path.join(folder,stratName))
        for line in lines[1:]:
            strategy.solvedProblems[line.split()[0]] = float(line.split()[1])+bias   
        strategies.append(strategy)
    return strategies    

def load_strategy(fileName):
    stratConfig = ConfigParser.SafeConfigParser()
    stratConfig.optionxform = str
    stratConfig.read(fileName)
    assert len(stratConfig.sections()) == 1
    stratName = stratConfig.sections()[0]
    strategy = Strategy(stratName,stratConfig.items(stratName))
    return strategy

class Strategy(object):
    '''
    Search Strategy
    '''

    def __init__(self,name,params):
        self.name = name
        self.parameters = {}
        self.solvedProblems = {}
        for param,val in params:
            self.parameters[param] = val
        self.runForFullTime = False
        self.runBefore = False       
        # Model fields    
        self.weights = None
        self.KM = None
        self.labels = None
        self.trainIndices = None
        self.bestKernelMatrixIndex = None
        self.minDataPoints = 5        

    def to_string(self):
        string = ''
        for param in sorted(self.parameters.keys()):
            string += '%s-%s ' % (param,str(self.parameters[param]))
        return string            

    def get_atp_string(self,atpConfig,time):        
        if (atpConfig.get('ATP Settings','strategy')=='Satallax'):
            strategyString = create_satallax_string(atpConfig.get('ATP Settings','binary'),self.name,self.parameters,self.runBefore)
            timeString = " ".join([atpConfig.get('ATP Settings','time'),str(time)])
            self.runBefore = True
        if (atpConfig.get('ATP Settings','strategy')=='E'):
            strategyString = " ".join([create_E_string(self.parameters),atpConfig.get('ATP Settings','default')])
            timeString = "".join([atpConfig.get('ATP Settings','time'),str(int(time+0.5))])        
        if (atpConfig.get('ATP Settings','strategy')=='Leo'):
            strategyString = " ".join([create_leo_string(self.parameters),atpConfig.get('ATP Settings','default')])
            timeString = " ".join([atpConfig.get('ATP Settings','time'),str(int(time+0.5))])    
        return strategyString,timeString

    def run(self,problem,runTime,atpConfig):
        if self.solvedProblems.has_key(problem.location):
            return True,self.solvedProblems[problem.location]        
            #strategyString = self.to_string() + ' -R'        
        if problem.bestTime == None or self.runForFullTime:
            time = runTime
        else:
            time = int(problem.bestTime)+1
        if problem.alreadyTried.has_key(self.name):
            if problem.alreadyTried[self.name] >= time:
                return False,problem.alreadyTried[self.name]
        strategyString,timeString = self.get_atp_string(atpConfig,time)            
        atp = RunATP(atpConfig.get('ATP Settings','binary'),strategyString,timeString,time,problem.location)        
        proofFound,_countersat,_output,time = atp.run()
        if proofFound:
            self.solvedProblems[problem.location] = time
        return proofFound,time

    def save(self,fileName):
        config = ConfigParser.SafeConfigParser()
        config.optionxform = str
        config.add_section(self.name)
        for param,val in self.parameters.items():
            config.set(self.name,param,str(val))
        with open(fileName, 'wb') as configfile:
            config.write(configfile)  

    def get_solved_in_time(self,time):
        solvedInTime = []
        for problem,problemTime in self.solvedProblems.iteritems():
            if problemTime < time:
                solvedInTime.append(problem)
        return set(solvedInTime)
   
    def copy(self):
        return copy.deepcopy(self)
            
    def __getstate__(self):        
        return dict(self.__dict__)

    def __setstate__(self, d):
        self.__dict__.update(d)      
        
    def create_model(self,trainProblems,KMs,regParams,cv,cvFolds):        
        self.trainIndices = []
        localLabels = []
        # Only learn from problem that can be solved
        for index,problemName in enumerate(trainProblems):
            if problemName in self.solvedProblems:
                self.trainIndices.append(index)
                localLabels.append(self.solvedProblems[problemName])
        self.labels = numpy.mat(localLabels).T
        # If there is not enough data, there is nothing to learn.
        if self.labels.shape[0] < self.minDataPoints: 
            self.bestKernelMatrixIndex = 0           
            return
        if cv:
            # Reduce KMs
            localKMs = []
            for KM in KMs:
                localKMs.append(KM[numpy.ix_(self.trainIndices,self.trainIndices)])
            bestKernelMatrixIndex,bestRegParam = cross_validate(self.labels,localKMs,cvFolds,regParams)
            self.bestKernelMatrixIndex = bestKernelMatrixIndex
            self.KM = localKMs[bestKernelMatrixIndex]            
        else:
            self.KM = KMs[0][numpy.ix_(self.trainIndices,self.trainIndices)] 
            self.bestKernelMatrixIndex = 0
            bestRegParam = regParams[0]
        # Add regularization
        for i in range(self.KM.shape[0]):
            self.KM[i,i] += bestRegParam 
            
        # Compute weights
        self.weights = self.KM.I * self.labels
    
    def update_model(self,newTrainProblemsWithOldIndices,oldIndicesToNewIndicesDict):
        deleteStrat = False
        # Delete all newly solved problems from the training data.        
        newTrainProblemsWithOldIndices = set(newTrainProblemsWithOldIndices)        
        localTrainIndices = []
        sliceIndices = []
        for position,index in enumerate(self.trainIndices):
            if index in newTrainProblemsWithOldIndices:
                localTrainIndices.append(oldIndicesToNewIndicesDict[index])
                sliceIndices.append(position)
        if len(sliceIndices) == 0:
                deleteStrat = True 
                return deleteStrat
        self.labels = self.labels[numpy.ix_(sliceIndices,[0])]
        self.trainIndices = localTrainIndices        
        if self.labels.shape[0] < self.minDataPoints:
            self.KM = None
            self.weighs = None            
        else:
            self.KM = self.KM[numpy.ix_(sliceIndices,sliceIndices)]
            self.weights = self.KM.I * self.labels
        return deleteStrat
    
    def predict(self,testKM):
        minVal = 300
        secondMin = 300
        for v in self.solvedProblems.itervalues():
            if v < minVal:
                secondMin = minVal
                minVal = v
        # If there is not enough data, return the maximal time.
        if self.labels.shape[0] < self.minDataPoints:
            #if secondMin == 300:
            #    return round(minVal+0.05,2)
            #else:
            #    return round(secondMin+0.05,2)
            # TODO: What's best?            
            return max(self.solvedProblems.itervalues())        
        localTestKM = testKM[numpy.ix_([0],self.trainIndices)]
        if (secondMin == 300) and (minVal == 300):
            returnVal = float(localTestKM*self.weights)
        elif secondMin == 300:
            returnVal = max(float(localTestKM*self.weights),minVal)
        else:
            returnVal = max(float(localTestKM*self.weights),secondMin)
        return returnVal               
        
        
    