age = int(input("Enter your age: "))
day = input("Enter weekday or weekend: ")

if age < 0:
    print("Age cannot be invalid")

if day != "weekday" and day != "weekend":
    print("Enter weekday or weekend")

if age >= 0 and (day == "weekday" or day == "weekend"):

    if age <= 12:
        group = "child"
        if day == "weekday":
            price = 6
        else:
            price = 8

    elif age <= 64:
        group = "adult"
        if day == "weekday":
            price = 11
        else:
            price = 14
    else: 
        group = "elder"
        if day == "weekday":
            price = 8
        else:
            price = 10
    print(f"Your {group} ticket costs {price} dollars.")