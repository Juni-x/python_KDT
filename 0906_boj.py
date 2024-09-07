'''n = int(input())

for i in range(1,n+1):
    print(i)'''
import sys
n = int(input())

for i in range(n):
    a, b =  map(int, sys.stdin.readline().split())
    print(a+b)