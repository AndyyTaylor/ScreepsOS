A = [
        [10, 30, 40],
        [20, 10, 60],
        [40, 50, 70]
    ]  # noqa

B = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

for x in range(3):
    for y in range(3):
        B[x][y] = A[y][x]
        print('x', x, 'y', y, '-', A[x][y])

for i in range(3):
    print(B[i][1])

print(A)
print(B)