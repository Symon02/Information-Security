import numpy as np
import sympy as sp
from Crypter import encrypt, decrypt, findSubkey, readFile

p = 11
task8NumKey = 5000

def mimAttack():
    plaintexts, cyphertexts = readFile('KPAdataD_japan/KPApairsD_non_linear.txt')
    decryptedCyph = {}
    cryptedPlain = {}
    keys1, keys2 = np.random.randint(0, 11, (task8NumKey, 4)), np.random.randint(0, 11, (task8NumKey, 4))
    k1Mat = []
    k2Mat =[]
    for k1 in keys1:
        k1Mat.append(findSubkey(k1, True))
    for k2 in keys2:
        k2Mat.append(findSubkey(k2, True))
    for plain in plaintexts:
        for i, intK in enumerate(k1Mat):
            intK = np.array(intK)
            e = encrypt(plain, intK, False, True)
            cryptedPlain[tuple(e.tolist())] = keys1[i]
    for cyph in cyphertexts:
        for i, extK in enumerate(k2Mat):
            extK = np.array(extK)
            d = decrypt(cyph, extK, False, True)
            decryptedCyph[tuple(d.tolist())] = keys2[i]
    common_keys = cryptedPlain.keys() & decryptedCyph.keys()
    internalKey = []
    externalKey = []
    for k in common_keys:
        print(cryptedPlain[k])
        internalKey.append(cryptedPlain[k])
        print(decryptedCyph[k])
        externalKey.append(decryptedCyph[k])
    return internalKey, externalKey