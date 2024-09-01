N = int(input())
ans = 0

for i in range(N):
    ans += (N-i)*(N-i)

print(ans)