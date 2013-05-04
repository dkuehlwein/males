'''
Created on May 4, 2013

@author: Daniel Kuehlwein
'''

from random import shuffle
from math import sqrt
import numpy,logging

def cross_validate(labels,KMs,cvFolds,regParams):
    logger = logging.getLogger(__file__)
    bestRegParam = None
    bestScore = 9000000000.0        
    # Create permutations for the cross validation
    permutations = []
    labelIndices = range(labels.shape[0])
    for _fold in range(cvFolds):        
        shuffle(labelIndices)
        trainSize = int(0.7 * labels.shape[0])
        trainPart = labelIndices[:trainSize]
        testPart = labelIndices[trainSize:]
        assert len(testPart) > 0
        assert len(trainPart) > 0
        permutations.append((trainPart,testPart))
    logger.debug('Starting CV.')
    for KMi,KM in enumerate(KMs):
        logger.debug('Starting loop for kernelMatrix '+str(KMi)) 
        scores = [0.0]*len(regParams)        
        for regIndex,regParam in enumerate(regParams):
            logger.debug('Starting loop for regParam '+str(regParam))
            score = 0.0
            regKM = KM.copy()
            for i in range(regKM.shape[0]):
                regKM[i,i] += regParam
            for (trainPart,testPart) in permutations:
                # Loop through strategies
                stratTrainKM = regKM[numpy.ix_(trainPart,trainPart)]
                stratTestKM = KM[numpy.ix_(testPart,trainPart)]
                stratTrainLabels = labels[numpy.ix_(trainPart,[0])]
                stratPredictions = stratTestKM * stratTrainKM.I * stratTrainLabels                    
                # Score
                stratTestLabels = labels[numpy.ix_(testPart,[0])]
                score += ((stratPredictions - stratTestLabels) * (stratPredictions - stratTestLabels).T)[0,0]
            
            score = sqrt(score/labels.shape[1])
            score = score/cvFolds
            logger.debug('Avg Error: '+str(score))
            scores[regIndex] += score
        for regIndex,regParam in enumerate(regParams):
            if scores[regIndex] < bestScore:
                    bestRegParam = regParam
                    bestKernelMatrixIndex = KMi
                    bestScore = scores[regIndex]
    logger.debug('Best KMIndex,regParam,error = %s / %s / %s' % (bestKernelMatrixIndex,bestRegParam,bestScore))
    return bestKernelMatrixIndex, bestRegParam