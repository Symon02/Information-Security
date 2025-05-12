from lab1Solver import encrypt, readFile, findSubkey
import math
from tqdm import tqdm
import numpy as np

l = 8
p = 11

def numberToBase(n, b):
    if n == 0: 
        return [0 for _ in range(l)]
    digits = []
    while n:
        digits.append(int(n%b))
        n //= b
    digits = digits[::-1]
    
    zeros = l - len(digits)
    
    num = [0 for _ in range(zeros)]
    for d in digits:
        num.append(d)
    
    return num

def main():
    plaintexts, cyphertexts = readFile('KPAdataD_japan/KPApairsD_nearly_linear.txt')
    
    pt = plaintexts[0]
    ct = cyphertexts[0]
    
    validKeys = []
    
    for n in tqdm(range(0,int(math.pow(p, l)))):
        k = numberToBase(n, p)
        en = encrypt(pt, findSubkey(k), True)
        
        if np.array_equal(en, ct):
            validKeys.append(k)
            print('Valid key found: ', k)

        

if __name__ == '__main__' :
    main()