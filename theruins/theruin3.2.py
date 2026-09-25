power = int(input())
key = str(input())

if power >= 50:
    if key == "gold":
        print("TEASURE")
    else:
        print("NEED KEY")
else:
    print("LOCKED")