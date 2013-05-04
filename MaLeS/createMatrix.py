'''
Created on Apr 27, 2012

Contains all function to create and update matrices.

@author: Daniel Kuehlwein
'''

from numpy import mat, zeros, exp, float64

def create_application_matrix_star(args):
    return create_application_matrix(*args)

def create_application_matrix(trainKeys,testKeys,featureDict,param):
    """ Creates a Kernel application matrix. 
    
    Entry i,j of the matrix is kernel(featureDict[trainKeys[i]],featureDict[testKeys[i]])
    """    
    rows = len(trainKeys)
    cols = len(testKeys)
    matrix = mat(zeros((rows,cols), dtype=float64))
    if trainKeys == testKeys:
        for i in range(rows): 
            for j in range(i,cols):
                x = featureDict[trainKeys[i]]
                y = featureDict[testKeys[j]]
                dot = x * x.T - 2 * x * y.T + y * y.T
                entry = exp(-dot/(2*(param**2)))
                matrix[i,j] = entry
                matrix[j,i] = entry
    else:
        for i in range(rows): 
            for j in range(cols):
                x = featureDict[trainKeys[i]]
                y = featureDict[testKeys[j]]
                dot = x * x.T - 2 * x * y.T + y * y.T
                entry = exp(-dot/(2*(param**2)))
                matrix[i,j] = entry
    return matrix
