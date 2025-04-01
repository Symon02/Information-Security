import numpy as np
import sympy as sp
from Crypter import encrypt, findSubkey, LinApproxBlocSNL

p=11

def findMatrixKey(NL = False):
    message = np.zeros(8)
    A = np.zeros((8,8))
    for i in range (0,8):
        #print("giro ",i,":")
        key = np.zeros(8)
        key[i] = 1
        #print("chiave generata: ", key)
        k = findSubkey(key)
        a = encrypt(message, k)
        #print("Linea generata: ", a)
        A[:,i] = a
    return A 

def findMatrixMessage(NL=False):
    key = np.zeros(8)
    k = findSubkey(key)
    B = np.zeros((8,8))
    for i in range(0,8):
        #print("giro ",i,":")
        message = np.zeros(8)
        message[i] = 1
        #print("messaggio generato: ", message)
        b = encrypt(message, k, NL)
        #print("Linea generata: ", b)
        B[:,i] = b
    return B

def modPMatrixInverter(matrix):
    matrix = np.array(matrix)
    sympyMat = sp.Matrix(matrix)
    RealInvMat = sympyMat.inv()
    #prova = RealInvMat@matrix
    #print("vediamo se worka:\n", prova)
    detMat = int(sympyMat.det())
    #print("determinante: ", detMat)
    SomeMat = RealInvMat*detMat
    invDet = pow(detMat, -1, p)
    invMatMod = np.mod(SomeMat*invDet, p)
    return invMatMod

def findMatrixC():
    C = np.zeros((8,8))
    for i in range(0,8):
        #print("giro ",i,":")
        message = np.zeros(8)
        message[i] = 1
        #print("messaggio generato: ", message)
        c = LinApproxBlocSNL(message)
        #print("Linea generata: ", b)
        C[:,i] = c
    return C%p

def testMat(A,B,C,plain,cypher,key, numbTry):
    ok = 0
    A = np.array(A)
    B = np.array(B)
    C = np.array(C)
    for u, x, k in zip(plain, cypher, key):
        u = np.array(u)
        x = np.array(x)
        k = np.array(k)
        out = A@k + B@u +C@x
        out = out.flatten()
        out =np.mod(out, p)
        #print(np.mod(np.sum(out), p))
        if np.mod(np.sum(out), p)==0:
            ok = ok+1
    return ok/numbTry