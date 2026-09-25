item = input("Your order: ")
price = float(input("Price: "))
quantity = int(input("Quantity: "))

subtotal = price*quantity
vat = subtotal*0.07
total = subtotal+vat

txt = "RECEIPT"
print(f"{txt:=^30}")
print(f"Item  : {item}")
print(f"Price  : {price:.2f} Baht")
print(f"Quantity : {quantity}")
print("-"*30)
print(f"Subtotal : {subtotal:.2f} Baht")
print(f"VAT 7% : {vat:.2f} Baht")
print(f"Total  : {total:.2f} Baht")
print("="*30)