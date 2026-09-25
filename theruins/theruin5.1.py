rows, columns = map(int, input().split())

count = 0
total = 0

for i in range(rows):
    values = list(map(int, input().split()))

    for j in range(columns):
        artifact = values[j]

        if 10 <= artifact <= 50:
            if artifact % 2 == 0:
                count += 1
                total += artifact

print(count)
print(total)