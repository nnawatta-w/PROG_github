weight = float(input("Enter your weight in kg.: "))
height_cen = float(input("Enter your height in cm.: "))

height_in_metres = height_cen/100
BMI = weight / (height_in_metres ** 2)

print(f"Your bmi : {BMI:.2f}")