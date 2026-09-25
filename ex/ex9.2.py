item = int(input())
pay = float(input())

if item > 5:
    if pay >= 500:
       print("Discount")
    else:
        print("No Discount")
else:
    print("Normal")