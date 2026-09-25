import random
numbers = []
for i in range(3):
    row = []
    for j in range (3):
        num = random.randint(1, 100)
        row.append(num)
    numbers.append(row)
print(numbers)