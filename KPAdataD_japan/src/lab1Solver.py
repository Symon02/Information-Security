import numpy as np
import sympy as sp

from Crypter import *
from MatrixOperation import *
from KPACryptoanalysis import *
from mimAttack import mimAttack

task6NumTry = 50000
p = 11
NL=False
NoLin=True
verbose = True

def main():
    
    lines, longKeys = readFile('KPAdataD_japan/KPApairsD_linear.txt')
    if NL:
        lines, longKeys = readFile('KPAdataD_japan/KPApairsD_nearly_linear.txt')
    if NoLin:
        lines, longKeys = readFile('KPAdataD_japan/KPApairsD_non_linear.txt')
    #lines, longKeys = readFile('KPAdataD_japan/checkNoLin.txt')
    #lines, longKeys = np.random.randint(0, 10, (task6NumTry, 8)), np.random.randint(0, 10, (task6NumTry, 8))
    keysMat = []
    if NL:
        lines = np.array(lines)       
        longKeys = np.array(lines)
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
    if NL:
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
    intKey, extKey = mimAttack()
    for ik, exk in zip(intKey, extKey):
        print("Internal key: ", ik, "\nExternal key: ", exk)
        """
    
    Internal key:  [6  5  9 10] 
    External key:  [0 0 3 5]

    Internal key:  [4 1 2 8]
    External key:  [0 0 4 0]

    Internal key:  [9 4 1 3]
    External key:  [9 6 4 6]
    """
    lines, longKeys = readFile('KPAdataD_japan/KPApairsD_non_linear.txt')
    k1 = findSubkey([4, 1, 2, 8], True)
    k2 = findSubkey([0, 0, 4, 0], True)
    plain = lines[0]
    e = encrypt(plain, k1, False, True)
    e2 = encrypt(e, k2, False, True)
    print(plain)
    print(e)
    print(e2)


        
if __name__ == '__main__':
    main()
