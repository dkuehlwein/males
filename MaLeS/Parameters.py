'''
Created on May 2, 2013

@author: Daniel Kuehlwein
'''

from random import randint,choice

class Parameter(object):
    '''
    Class for a parameter of an ATP.
    '''
    def __init__(self,values):
        '''
        Constructor
        @param values: The possible values for this parameter
        '''        
        self.values = values
        
    def pick_random_value(self):
        index = randint(0,len(self.values)-1)
        return self.values[index]
        

        
class Parameters(object):
    '''
    Class contains all E Parameters
    '''

    def __init__(self,atpConfig):
        '''
        Constructor
        '''
        self.knownStrategies = {}
        self.newStratCounter = 0
        self.parameters = {}
        if atpConfig.has_section('Boolean Parameters'):
            for option in atpConfig.options('Boolean Parameters'):
                #self.parameters[('BP',option)] = Parameter([True,False])
                self.parameters[option] = Parameter([True,False])
        
        if atpConfig.has_section('Int Min Parameters'):
            for option in atpConfig.options('Int Min Parameters'):
                minVal = atpConfig.getint('Int Min Parameters',option)
                maxVal = atpConfig.getint('Int Max Parameters',option)
                if minVal == maxVal:
                    #self.parameters[('Int',option)] = Parameter([minVal])
                    self.parameters[option] = Parameter([minVal])
                else:
                    self.parameters[option] = Parameter(range(minVal,maxVal))

    def perturb(self,strategy,walkLength):
        newStrategy = strategy.copy()
        for _i in range(walkLength):
            param = choice(self.parameters.keys())
            newVal = self.parameters[param].pick_random_value()
            newStrategy.parameters[param] = newVal
        newStratString = newStrategy.to_string()
        if self.knownStrategies.has_key(newStratString):
            newStrategy.name = self.knownStrategies[newStratString]
        else:
            newStrategy.name = 'NewStrategy%s' % self.newStratCounter
            self.newStratCounter += 1
            self.knownStrategies[newStratString] = newStrategy.name            
        return newStrategy
    
    def add_strategy(self,strategy):
        self.knownStrategies[strategy.to_string()] = strategy.name
    
    def __getstate__(self):        
        return dict(self.__dict__)

    def __setstate__(self, d):
        self.__dict__.update(d) 

        