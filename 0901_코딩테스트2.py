a, b = map(int, input().split())
d = int(input())

for i in range(d):
    if i % 2 == 0:
        if a/2 > a//2:
            b += a//2 +1
        else: b += a//2
        a = a//2
    else:
        if b/2 > b//2:
            a += b//2 + 1
        else: a += b//2
        b = b//2

print(a, b)