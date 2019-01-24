from decimal import Decimal

M1 = []
M2 = []
Ad = []
m = 0

x = Decimal(1)
y = Decimal(-1)

dx = None
dy = None
temp_0 = Decimal(0)
temp_1 = Decimal(0)

h = None
H = None
prob = None

sum_1 = None
chk = Decimal(-1)
s = None
prev = Decimal(0)
trunc = 10

# Assigns value of the input given to sigmoid function 
def assgH(p):
    global H  
    global prob                                   
    h = (M2[p]*M1[p]*Decimal("0.0001")*x + y )
    H = round(( h.exp()/( Decimal(1) + h.exp() )) , 2 )
    prob = H
    if H>=Decimal(0.5):
       H = Decimal(1)
    else:
       H = Decimal(0) 

#gets the sum of cost function over the range of inputs 
def getJ(q):
    sum_1 = Decimal(0)
    if q != 0:
       for i in range(m):
           assgH(i)
           sum_1 += Decimal( ( prob - Ad[i] )*M1[i]*M2[i] )
    else:
       for i in range(m):
           assgH(i)
           sum_1 += Decimal( prob - Ad[i] )
    return sum_1

print( "Welcome to the Admission predictor v1.0.0.1!" )

# Input Loop
with open('Admissions.txt') as file:
    for line in file:
        M1.append(Decimal(line.split(",")[0]))
        M2.append(Decimal(line.split(",")[1]))
        Ad.append(Decimal(line.split(",")[2]))
        m += 1

while round(chk, trunc) != Decimal(0):
    dy = getJ(0)
    dx = getJ(1)
    prev = dy + dx 
    temp_2 = x - ( Decimal(0.001) * dx/Decimal(m))
    temp_1 = y - ( Decimal(0.001) * dy/Decimal(m))
    x = temp_2
    y = temp_1
    chk = ( getJ(0) + getJ(1) - prev )
    # print( str(Decimal(x)) + " " + str(Decimal(y)) )

print( "\nLearning Complete! Ready to Predict!\n" )

# user input loop
while s != "0":
    m = m + 1
    M1.append(0)
    M2.append(0)
    Ad.append(0)
    M1.insert( m, Decimal(input("Enter marks of examination 1: ")) )
    M2.insert(m, Decimal(input("Enter marks of examination 2: ")) )
    assgH(m)
    Ad.insert(m, H)
    
    if H==Decimal(0): 
        print( "Probability of Getting Admitted is " + str(round(Decimal( prob*100 ),2)) + "%") 
        print("According to the predictor, the student will not be admitted.")
        
    else:
        print( "Probability of Getting Admitted is " + str(round(Decimal( prob*100 ), 2))+ "%") 
        print("According to the predictor, the student will be admitted.")

    s = input("Enter 0 To Exit The Program ")

