import numpy as np
import sympy as sp

task6NumTry = 50000
p = 11

def readFile(path) :
    keys = []
    lines = []
    
    with open(path, 'r') as file :
        for row in file:
            l = row.split('\t')[0]
            k0 = row.split('\t')[1]
                
            for c in ['[', ']', '\n']:
                l = l.replace(c, '')
                k0 = k0.replace(c, '')
                
            l = l.split(',')
            k0 = k0.split(',')
            k0 = list(map(lambda x: int(x), k0))
            l = list(map(lambda x: int(x), l))
            #k = findSubkey(k0)
            lines.append(l)
            keys.append(k0)
            
    return lines, keys

def findSubkey(key):
    k0= np.array(key)
    k1 = [k0[0], k0[2], k0[4], k0[6]]
    k2 = [k0[0], k0[1], k0[2], k0[3]]
    k3 = [k0[0], k0[3], k0[4], k0[7]]
    k4 = [k0[0], k0[3], k0[5], k0[6]]
    k5 = [k0[0], k0[2], k0[5], k0[7]]
    k6 = [k0[2], k0[3], k0[4], k0[5]]
    
    k = []
    k.append(k1)
    k.append(k2)
    k.append(k3)
    k.append(k4)
    k.append(k5)
    k.append(k6)
    return k

def encrypt(line, key, NL = False):
    key = np.array(key)
    line = np.array(line)
    for i in range(0,4):
        if i==0:
            v = sum(line, key[i])
        else:
            v = sum (w, key[i])
        if NL:
            y = blockSNL(v)
        else:
            y = blockS(v)
        z = blockT(y)
        w = blockL(z)
    v_fin = sum(w, key[4])
    if NL:
        y_fin = blockSNL(v_fin)
    else:
        y_fin = blockS(v_fin)
    z_fin = blockT(y_fin)
    x = sum(z_fin, key[5])
    return x

def decrypt(x, keys, NL = False):
    keys = np.array(keys)
    z = sottraction(x, keys[-1])
    y = invBlockT(z)
    if NL:
        v= invBlockSNL(y)
    else:
        v = invBlockS(y)
    for i in range(2,6):
        if i==2:
            w = sottraction(v, keys[-i])
            z1 = invBlockL(w)
            y1 = invBlockT(z1)
            if NL:
                v1 = invBlockSNL(y1)
            else:
                v1 = invBlockS(y1)
        else:
            w = sottraction(v1, keys[-i])
            z1 = invBlockL(w)
            y1 = invBlockT(z1)
            if NL:
                v1 = invBlockSNL(y1)
            else:
                v1 = invBlockS(y1)

    u = sottraction(v1, keys[0])
    return u

def blockS(input):
    input= np.array(input)
    out = np.mod(2*input, p)
    return out

def invBlockS(input):
    input= np.array(input)
    out = np.mod(6*input, p)
    return out

def blockT (input):
    input = np.array(input)
    out = input[0:4]
    input = np.flip(input)
    out = np.hstack((out, input[0:4]))
    return out

def invBlockT(input):
    input = np.array(input)
    out = input[0:4]
    input = np.flip(input)
    out = np.hstack((out, input[0:4]))
    return out

def blockL(input):
    input = np.array(input)
    Matrix = [[2,5],[1,7]]
    input = input.reshape(2,4)
    Matrix = np.array(Matrix)
    out = np.mod(Matrix@input, p)
    out = out.flatten()
    return out

def invBlockL(input):
    input = np.array(input)
    invMatrix = [[2,8],[6,10]]
    input = input.reshape(2,4)
    invMatrix = np.array(invMatrix)
    out = np.mod(invMatrix@input, p)
    out = out.flatten()
    return out

def sottraction(input, key):
    input = np.array(input)
    key = np.array(key)
    out = input - np.hstack((key, key))
    out = np.mod(out, p)
    return out

def sum(input, key):
    input = np.array(input)
    key = np.array(key)
    out = input + np.hstack((key, key))
    out = np.mod(out, p)
    return out

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
    return A%p  

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
    return B%p

def modPMatrixInverter(matrix, p):
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

def KPACryptoanalysisLinear(texts, cyphers):
    matA = findMatrixKey()
    matA =np.array(matA)
    invA = modPMatrixInverter(matA, p)
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

def blockSNL(input):
    input = np.array(input).astype(int)
    switches = [0,2,4,8,6,10,1,3,5,7,9]
    switches = np.array(switches)
    out = [switches[n] for n in input]
    return np.array(out)

def invBlockSNL(input):
    input = np.array(input).astype(int)
    invSwitches = [0,6,1,7,2,8,4,9,3,10,5]
    invSwitches = np.array(invSwitches).astype(int)
    out = [invSwitches[n] for n in input]
    return np.array(out).astype(int)

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

def LinApproxBlocSNL(input):
    input = np.array(input).astype(int)
    out = []
    for n in input:
        value = (n-(11-n)) % p
        out.append(value)
    out = np.array(out)
    return out

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
 
def KPACryptoanalysisNearLinear(texts, cyphers):
    matA = findMatrixKey(NL = True)
    matA =np.array(matA)
    invA = modPMatrixInverter(matA, p)
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

def main():
    #lines, longKeys = readFile('KPAdataD_japan/KPApairsD_linear.txt')
    #lines, longKeys = readFile('KPAdataD_japan/check.txt')
    lines, longKeys = readFile('KPAdataD_japan/KPApairsD_nearly_linear.txt')
    keysMat = []
    #print("Inizio a creare i vettori")
    #lines, longKeys = np.random.randint(0, 10, (task6NumTry, 8)), np.random.randint(0, 10, (task6NumTry, 8))
    lines = np.array(lines)
    longKeys = np.array(lines)
    cyphArr = np.zeros((task6NumTry,8))
    #print("finito di creare i vettori")
    for i, k in enumerate(longKeys):
        #print("Separo la chiave: ", i)
        keysMat.append(findSubkey(k))
    #print("Finito di creare le sottochiavi")
    for z, (line, keys) in enumerate(zip(lines, keysMat)):
        #print("Cripto la inea: ", z)
        i = 0
        #print("plaintext: ", line)
        e = encrypt(line, keys, True)
        cyphArr[i,:] = e
        i+=1
        #print("encrypting:", e)
        d =decrypt(e,keys, True)
        #print("decrypting: ", d, "\n")
    matA = findMatrixKey(True)
    #print("Matrice A relativa alle chiavi:\n", matA.astype(int))
    matB = findMatrixMessage(True)
    #print("Matrice B relativa ai messaggi:\n", matB.astype(int))
    """
    possibleLinearK = KPACryptoanalysisLinear(lines, longKeys)
    for i, k in enumerate(possibleLinearK):
        print("Possibile chiave numero ", i, ":\n", k) 
    #[6.00000002; 5.99999997; 4.99999999; 3.99999998; 5.99999999; 5.00000004;  2.     ;    8.      ] 
    # --> possible key [6;6;5;4;6;5;2;8]

    #code to test that the key founded is the right one
    k = findSubkey([6,6,5,4,6,5,2,8])
    for text in lines:
        prova = encrypt(text, k)
        print(prova)
    """
    matC = findMatrixC()
    #print("Mst A:\n", matA, "\nMat B:\n", matB, "\nMat C:\n", matC)
    prob = testMat(matA,matB,matC,lines,cyphArr,longKeys,task6NumTry)
    #print("Our probability: ",prob, "\nTreshold probability: ", (1/p**8))

    """
    """
    possibleNLKey = KPACryptoanalysisNearLinear(lines, longKeys)
    for i, k in enumerate(possibleNLKey):
        print("Possibile chiave numero ", i+1, ":\n", list(map(round, k)))
    
    """
    [7, 4, 3, 3, 6, 2, 7, 4]
    [9, 3, 9, 5, 9, 6, 4, 9]
    [9, 7, 9, 2, 10, 6, 7, 4]   --> actual key = [7,6,3,9,0,9,2,9]
    [0, 0, 0, 4, 0, 6, 2, 5]
    [6, 7, 6, 8, 1, 3, 3, 3]
    """

    k = findSubkey([7,6,3,9,0,9,2,9])
    for text in lines:
        prova = encrypt(text, k, NL = True)
        #print(prova)
"""
[ 0 10  6  5 10  3  5  6]
[ 6  7  0  9  7 10  0  3]
[ 8  5 10  7  4  2  2  5]
[10  7  9 10  4  3  7 10]
[0 5 0 9 2 2 3 8]
"""

if __name__ == '__main__':
    main()
