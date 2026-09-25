data = input().split()

rows = int(data[0])
columns = int(data[1])
target = int(data[2])

vulnerable_count = 0
greatest_total = 0

for i in range(rows):
    values = input().split()

    row_total = 0

    for j in range(columns):
        row_total = row_total + int(values[j])

    if row_total >= target:
        vulnerable_count = vulnerable_count + 1

        if row_total > greatest_total:
            greatest_total = row_total

print(vulnerable_count)
print(greatest_total)