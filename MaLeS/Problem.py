'''
Created on Jul 27, 2012

@author: Daniel Kuehlwein
'''

def getAllProblems(problemFile):
    allProblems = []
    IS = open(problemFile,'r')
    for line in IS:
        line = line.strip()
        if not line == '':
            allProblems.append(Problem(line))
    IS.close()
    return allProblems

class Problem(object):
    '''
    Class for a single TPTP Problem.
    '''

    def __init__(self,location):
        '''
        Constructor
        '''
        self.location = location
        self.bestTime = None
        self.bestStrategy = None
        self.bestStrategyName = None
        self.alreadyTried = {}
        
    def addStrategy(self,strategy,time):
        self.alreadyTried[strategy.name] = time
    
    def __getstate__(self):        
        return dict(self.__dict__)

    def __setstate__(self, d):
        self.__dict__.update(d) 
        