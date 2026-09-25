def calculate_commission(total_sales: float, commission_rate: float = 0.05) -> float:
    return total_sales * commission_rate

check_target = lambda total_sales, sales_target=50000.0: total_sales >= sales_target

def calculate_total_income(base_salary: float, commission: float, bonus: float) -> float:
    return base_salary + commission + bonus

def calculate_projeted_income(monthly_income: float, months: int) -> float:
    if months <= 0:
        return 0.0
    return monthly_income + calculate_projeted_income(monthly_income, months - 1)

def print_report(name, total_sales, commission, bonus, total_income, target_reached, projected_income):
    print("\nSales commission report")
    print(f"Employee: {name}")
    print(f"Total sales: {total_sales:.2f} THB")
    print(f"Commission: {commission:.2f} THB")
    print(f"Bonus: {bonus:.2f} THB")
    print(f"Total income: {total_income:.2f} THB")
    print(f"Sales target reached: {'Yes' if target_reached else 'No'}")
    print(f"Projected income: {projected_income:.2f} THB")

employee_name = input("Employee name: ")
base_salary = float(input("Base monthly salary: "))
total_sales = float(input("Total monthly sales: "))
months = int(input("Projection months: "))

commission = calculate_commission(total_sales)

target_reached = check_target(total_sales)
if target_reached:
    bonus = 2000.0
else:
    bonus = 0.0

total_income = calculate_total_income(base_salary, commission, bonus)

projected_income = calculate_projeted_income(total_income, months)

print_report(employee_name, total_sales, commission, bonus, total_income, target_reached, projected_income)