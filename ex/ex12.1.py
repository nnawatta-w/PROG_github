import math
import random

participants = int(input("Enter the number of participants: "))
winners = int(input("Enter the number of winners: "))

tickets = list(range(1, participants + 1))

sheet = math.ceil(participants / 8)
prize = math.floor(8888/winners)

winning_ticket = random.sample(tickets, winners)

print(f"Ticket sheets needed: {sheet}")
print(f"Prize per winner: {prize} THB")
print(f"Winning tickets: {winning_ticket}")