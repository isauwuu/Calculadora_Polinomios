import math

def divisores(x:int) -> list[int]:
    x=abs(x)
    if x==0: return []
    l:set[int]=set()
    for i in range(1,math.isqrt(x)+1):
        if x%i==0:
            l.update([i,-i,x//i,-(x//i)])
    return sorted(l)

if __name__ == '__main__':
    print(divisores(-100))