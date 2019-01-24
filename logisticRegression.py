from decimal import *


pop = []
profit = []
y = None
x = None
nxt = None
a = None
b = None
dy = None
dx = None
s = None
prev = None
chk = Decimal(-1)
m = 0


trunc = 5
res = Decimal(10 ** (-trunc))


def getj(p,q):
    sum_1 = Decimal(0)
    for j in range(p):
        sum_1 += (x + y*pop[j] - profit[j])*(pop[j] ** q)
    return sum_1

print("Welcome to the Profit Maximizer v1.0.1")


with open('ExamplesPop.txt') as f:
    for line in f:
        pop.append(Decimal(line))
        m += 1
with open('ExamplesProfits.txt') as f:
    for line in f:
        profit.append(Decimal(line))

y = ((profit[1] - profit[0])/(pop[1] - pop[0]))
x = (profit[0] - y * pop[0])

print("Running Learning Algorithm, Please Wait...")

while round(chk, trunc) != Decimal(0):
    dy = getj(m, 1)
    dx = getj(m, 0)
    prev = (dy + dx)
    a = x - (res * dx/Decimal(m))
    b = y - (res * dy/Decimal(m))
    x = a
    y = b
    chk = (getj(m, 0) + getj(m, 1) - prev)
    print("Progress: " + str(round(Decimal(100) - (chk * Decimal(10 ** trunc)), 2)) + "%", end = '\r')

print("Learning Complete! Ready To Predict\n")

while s != "0":
    nxt = Decimal(input("Enter The Population Of The Next City (in 10,000 People): "))
    print("The Algorithm Predicts a Profit of (in 10,000 USD): " + str(round((x + y * nxt), trunc)))
    s = input("Enter 0 To Exit The Program\n")

