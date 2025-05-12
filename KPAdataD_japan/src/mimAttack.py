import numpy as np
import sympy as sp
from Crypter import encrypt, decrypt, findSubkey, readFile

p = 11

def key_gen():
    key = np.random.randint(0, p, 4)
    return key


def mitmAttack():
    u1 = [6,3,5,2,0,2,3,4]
    x1 = [1,1,10,8,4,3,7,3]
    dictionary_1 = {}
    dictionary_2 = {}

    thousand_keys_1 = []
    for i in range(0, 80000):
        thousand_keys_1.append(key_gen())

    thousand_keys_1 = np.array(thousand_keys_1)
    thousand_keys_1 = np.unique(thousand_keys_1, axis=0).tolist()
    print(len(thousand_keys_1))

    thousand_keys_2 = []
    for i in range(0, 80000):
        thousand_keys_2.append(key_gen())

    thousand_keys_2 = np.array(thousand_keys_2)
    thousand_keys_2 = np.unique(thousand_keys_2, axis=0).tolist()
    print(len(thousand_keys_2))

    for i in range(0, len(thousand_keys_1)):
        k1 = findSubkey(thousand_keys_1[i], True)
        dictionary_1[i] = encrypt(u1, k1, False, True)
    
    for i in range(0, len(thousand_keys_2)):
        k2 = findSubkey(thousand_keys_2[i], True)
        dictionary_2[i] = decrypt(x1, k2, False, True)

    dict(sorted(dictionary_1.items(), key=lambda item: item[1].all()))
    dict(sorted(dictionary_2.items(), key=lambda item: item[1].all()))

    for i in range(0, len(thousand_keys_1)):
        for j in range(0, len(thousand_keys_2)):
            if np.array_equal(dictionary_1[i], dictionary_2[j]):
                print("Found a match!")
                print("Key 1 = ", thousand_keys_1[i])
                print("Key 2 = ", thousand_keys_2[j])
                print("Ciphertext = ", dictionary_1[i])
                print("Plaintext = ", dictionary_2[j])
                break
