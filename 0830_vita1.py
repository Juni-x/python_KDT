"""
입력:
첫째 줄에 정수 N이 주어집니다.
둘째 줄부터 N개의 줄에 걸쳐 영어 대소문자와 숫자, 공백 및 특수문자 등이 포함된 문장이 주어지며, 각 문장의 길이는 1자 이상 255자 이하입니다.

출력:
N개의 줄에 걸쳐 각 문장에서 모음만을 순서대로 출력합니다.
단, 모음이 한 개도 없으면 ???을 출력합니다.
"""

N = int(input())

for i in range(N):
	ans = []
	words = list(input())
	
	for j in words:
		if j in ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']:
			ans.append(j)
	
	if ans == []:
		print("???")
	else:
		print(''.join(ans))