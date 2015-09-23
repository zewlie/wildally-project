import random
playing = "Yes"
num_tries = 0
high_score = float('inf')
while playing == "Yes":
    print "What is your name?"
    name = raw_input("(type in your name)")
    print "%s, I am thinking of a number between 1 and 100. Try to guess my number." %(name)
    random_number = random.randint(1, 100)


    user_number = 0
    
    print random_number
    while True:
        try :
            user_number = int(raw_input("What do you think my number is?"))
            if user_number < 1 or user_number > 100:
                print "Please guess a number between 1 and 100"
                user_number = int(raw_input("What do you think my number is?"))
            num_tries+=1
            if user_number == random_number:
                print "Your guess is correct, it took you %d tries" %(num_tries)
                if num_tries < high_score:
                    print "HIGH SCORE"
                    high_score = num_tries
                playing = raw_input("Do you want to play again? Type Yes or No")
                if playing == "No":
                    break
                else:
                    num_tries = 0
                    random_number = random.randint(1, 100)
                    user_number = 0
                    print random_number
            elif user_number > random_number:
                print "Your guess is too high"
            else: 
                print "Your guess is too low"
        except ValueError:
            print "Please enter an integer"
        
