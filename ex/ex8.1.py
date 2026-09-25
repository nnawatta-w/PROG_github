scores = [[85, -1, 90],
          [-1, 78, 12],
          [54, 66, 31],
          [-1, 56, -1]]
total = 0
for row in scores:
        for i in row:
            total += i 
print(total)
