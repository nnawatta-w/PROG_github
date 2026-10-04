def sum(x):
    total = 0
    for num in x:
        total += num
    return total

def count(x):
    total = 0
    for num in x:
        total += 1
    return total

def max(x):
    maximum = x[0]
    for num in x:
        if num > maximum:
            maximum = num
    return maximum

def min(x):
    minimum = x[0]
    for num in x:
        if num < minimum:
            minimum = num
    return minimum

def average(x):
    total = 0
    for num in x:
        total += num
    return total / count(x)