x = int(input("Enter number of seeds to buy: "))
total_cost = 9000000000*(1.05**x-1)/0.05
print(int(total_cost))