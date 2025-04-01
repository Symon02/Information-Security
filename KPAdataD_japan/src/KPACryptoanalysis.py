import numpy as np
import sympy as sp

from MatrixOperation import findMatrixC, findMatrixKey, findMatrixMessage, modPMatrixInverter


p=11

def KPACryptoanalysisNearLinear(texts, cyphers):
    matA = findMatrixKey(NL = True)
    matA =np.array(matA)
    invA = modPMatrixInverter(matA)
    invA = np.array(invA)
    matB = findMatrixMessage(NL = True)
    matB = np.array(matB)
    matC = findMatrixC()
    matC = np.array(matC)
    matA,matB,matC = matA%p, matB%p, matC%p
    keys = np.zeros((5,8))
    for i, (u, x) in enumerate(zip(texts, cyphers)):
        u = np.array(u)
        x = np.array(x)
        tmp = ((matB@u)%p).flatten()
        tmp2 = ((matC@x)%p).flatten()
        finTemp = ((tmp2 - tmp)%p)
        k = ((invA@finTemp)%p).flatten()
        keys[i,:] = k%p 
    return keys%p

def KPACryptoanalysisLinear(texts, cyphers):
    matA = findMatrixKey()
    matA =np.array(matA)
    invA = modPMatrixInverter(matA)
    invA = np.array(invA)
    matB = findMatrixMessage()
    matB = np.array(matB)
    keys = np.zeros((5,8))
    for i, (t, c) in enumerate(zip(texts, cyphers)):
        t = np.array(t)
        c =np.array(c)
        tmp = np.mod(matB@t, p).flatten()
        tmp = np.mod(c - tmp, p)
        k = np.mod(invA@tmp, p).flatten()
        keys[i,:] = k
    return keys