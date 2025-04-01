import numpy as np
import sympy as sp
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

def LinApproxBlocSNL(input):
    input = np.array(input).astype(int)
    out = []
    for n in input:
        value = (n-(11-n)) % p
        out.append(value)
    out = np.array(out)
    return out