from calculation import calculate_total
from receipt import print_receipt

prices = [20, 35, 15]

total = calculate_total(prices)
print_receipt("Guide", total)