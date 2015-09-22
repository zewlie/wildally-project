import random

print "What is your name?"
name = raw_input("(type in your name)")
print "%s, I am thinking of a number between 1 and 100. Try to guess my number." %(name)
random_number = random.randint(1, 100)

user_number = 0
num_tries = 0
print random_number
while True:
    user_number = int(raw_input("What do you think my number is?"))
    num_tries+=1
    if user_number == random_number:
        print "Your guess is correct, it took you %d tries" %(num_tries)
        break
    elif user_number > random_number:
        print "Your guess is too high"
    else: 
        print "Your guess is too low"
    
