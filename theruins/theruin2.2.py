length = float(input("Enter the length: "))
material = input("Enter material: ")

valid = length < 2.5 and material in ["bronze", "copper", "silver"]
print(valid)