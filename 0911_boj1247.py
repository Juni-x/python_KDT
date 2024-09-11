import sys


for i in range(3):
    n = int(sys.stdin.readline())
    sum_num = 0
    for j in range(n):
        m = int(sys.stdin.readline())
        sum_num += m
    if sum_num == 0:
        print('0')
    elif sum_num > 0:
        print('+')
    else:
        print('-')
