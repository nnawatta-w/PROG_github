numbers = [[5, 10, 15],
           [20, 3, 7],
           [8, 12, 10],
           [30, 5, 2]]
max_sum = 0

for row in numbers:
    row_sum = 0
    for num in row:
        row_sum += num
    if row_sum > max_sum:
        max_sum = row_sum
print("Max sum of row is: ", max_sum)