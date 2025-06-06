import numpy as np
import sympy as sp

from Crypter import *
from MatrixOperation import *
from KPACryptoanalysis import *
from mimAttack import mitmAttack
import argparse
task6NumTry = 50000
p = 11
NL=True
NoLin=False
verbose = True

def main():
    
    parser = argparse.ArgumentParser(description='Lab1Solver.')
    parser.add_argument('-v', '--verbose', '-VERBOSE', action='store_true', help='Enable verbose output')
    parser.add_argument('-nl', '--nearlylinear', '-NEARLYLINEAR', action='store_true', help='Enable nearly linear mode')
    parser.add_argument('-NL', '--nonlinear', '-NONLINEAR', action='store_true', help='Enable non-linear mode')
    args = parser.parse_args()
    
    verbose = args.verbose
    NL = args.nearlylinear
    NoLin = args.nonlinear

    lines, longKeys = readFile('KPAdataD_japan/KPApairsD_linear.txt')
    if NL:
        lines, longKeys = readFile('KPAdataD_japan/KPApairsD_nearly_linear.txt')
    if NoLin:
        lines, longKeys = readFile('KPAdataD_japan/KPApairsD_non_linear.txt')
    lines, longKeys = readFile('KPAdataD_japan/check.txt')
    #lines, longKeys = np.random.randint(0, 10, (task6NumTry, 8)), np.random.randint(0, 10, (task6NumTry, 8))
    lines, longKeys = readFile('KPAdataD_japan/KPApairsD_nearly_linear.txt')
    keysMat = []
    #f NL:
        #lines = np.array(lines)       
        #longKeys = np.array(lines)
    cyphArr = np.zeros((task6NumTry,8))
    for k in longKeys:
        keysMat.append(findSubkey(k,NoLin))
    for i, (line, keys) in enumerate(zip(lines, keysMat)):
        i = 0
        if verbose : print("plaintext: ", line)
        e = encrypt(line, keys, NL=NL, NoLin=NoLin)
        cyphArr[i,:] = e
        i+=1
        if verbose : print("encrypting:", e)
        d = decrypt(e ,keys, NL=NL, NoLin=NoLin)
        if verbose : print("decrypting: ", d, "\n")
    LinMatA = findMatrixKey()
    if verbose : print("Mat A:\n", LinMatA.astype(int))
    LinMatB = findMatrixMessage()
    if verbose : print("Mat B:\n", LinMatB.astype(int))
    possibleLinearK = KPACryptoanalysisLinear(lines, longKeys)
    for i, k in enumerate(possibleLinearK):
        print("Possible key for linear function number ", i+1, ":\n", list(map(round, k))) 

    #possible key [6;6;5;4;6;5;2;8]

    #code to test that the key founded is the right one
    k = findSubkey([6,6,5,4,6,5,2,8])
    print("Cryping with the finded linear key:\n")
    for text in lines:
        prova = encrypt(text, k)
        print(prova)
    

    #Start Near Linear Task --> Change the NL variable at the top of the file
    lines, longKeys = readFile('KPAdataD_japan/KPApairsD_nearly_linear.txt')
    if True:
        NLmatA = findMatrixKey(NL)
        NLmatB = findMatrixMessage(NL)
        NLmatC = findMatrixC()
        cyphArr = np.array(cyphArr)
        if verbose : print("NL Mat A:\n", NLmatA, "\nNL Mat B:\n", NLmatB, "\nNL Mat C:\n", NLmatC)
        prob = testMat(NLmatA,NLmatB,NLmatC,lines,cyphArr,longKeys,task6NumTry)
        print("Our probability: ",prob, "\nTreshold probability: ", (1/p**8))

        possibleNLKey = KPACryptoanalysisNearLinear(lines, longKeys)
        for i, k in enumerate(possibleNLKey):
            print("Possible key for NL number ", i+1, ":\n", list(map(round, k)))
        
        """
        POSSIBLE NL KEYS:
            [7, 4, 3, 3, 6, 2, 7, 4]
            [9, 3, 9, 5, 9, 6, 4, 9]
            [9, 7, 9, 2, 10, 6, 7, 4]   --> actual key = [7,6,3,9,0,9,2,9]
            [0, 0, 0, 4, 0, 6, 2, 5]
            [6, 7, 6, 8, 1, 3, 3, 3]

        """
        #actual key test. It was finded by brute force
        k = findSubkey([7,6,3,9,0,9,2,9])
        print("Cryping with the finded near linear key:\n")
        for text in lines:
            prova = encrypt(text, k, NL = True)
            print(prova)
    intKey, extKey = mitmAttack()
    for ik, exk in zip(intKey, extKey):
        print("Internal key: ", ik, "\nExternal key: ", exk)
        

    lines, longKeys = readFile('KPAdataD_japan/KPApairsD_non_linear.txt')

    # Testing if the pairs of keys founded by mitm attack are actually the correct ones
    k1 = findSubkey([0, 5, 4, 0], True)    
    k2 = findSubkey([10, 8, 0, 6], True)
    for line, cypher in zip(lines, longKeys): 
        print("plain: ", line)
        e = encrypt(line, k1, False, True)
        print("e:", e)
        e2 = encrypt(e, k2, False, True)
        print("e2: ", e2)
        print("Actual encryption: ", cypher)


        
if __name__ == '__main__':
    main()
