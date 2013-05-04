'''
Created on May 2, 2013

@author: Daniel Kuehlwein
'''

import copy,os,ConfigParser
from RunATP import RunATP

def create_E_string():
    #baseDir = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return 'foo'

def create_satallax_string(binary,name,parameters,runBefore):    
    if not runBefore:
        binDir = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(binary))))    
        modesDir = os.path.join(binDir,'modes')
        modeFile = os.path.join(modesDir,name)    
        OS = open(modeFile,'w')
        for param,val in parameters.items():
            OS.write(param+'\n')            
            OS.write(str(val).lower()+'\n')
        OS.close()
    return '-m %s' % name
    

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

    def to_string(self):
        string = ''
        for param in sorted(self.parameters.keys()):
            string += '%s-%s ' % (param,str(self.parameters[param]))
        return string            

    def run(self,problem,runTime,atpConfig):
        if self.solvedProblems.has_key(problem.location):
            return True,self.solvedProblems[problem.location]
        
        if (atpConfig.get('ATP Settings','strategy')=='Satallax'):
            strategyString = create_satallax_string(atpConfig.get('ATP Settings','binary'),self.name,self.parameters,self.runBefore)
            self.runBefore = True
        if (atpConfig.get('ATP Settings','strategy')=='E'):
            strategyString = create_E_string(self.name,self.parameters)
            strategyString = self.to_string() + ' -R'
        if problem.bestTime == None or self.runForFullTime:
            time = runTime
        else:
            time = int(problem.bestTime)+1
        if problem.alreadyTried.has_key(self.name):
            if problem.alreadyTried[self.name] >= time:
                return False,problem.alreadyTried[self.name]
        atp = RunATP(atpConfig.get('ATP Settings','binary'),strategyString,atpConfig.get('ATP Settings','time'),time,problem.location)        
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
        
        
    