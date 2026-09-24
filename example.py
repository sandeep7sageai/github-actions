'''
Example python code to check the lint.yml workflow
'''
# Ask the user for their name and age
name = input("What is your name? ")
age = int(input("How old are you? "))  # Convert input string to an integer

# Calculate years until they turn 50
years_to_50 = 50 - age

# Print a dynamic message using an f-string
if years_to_50 > 0:
    print(f"Hello {name}! You have {years_to_50} years left until you turn 50.")
else:
    print(f"Hello {name}! You already turned 50 {-years_to_50} years ago!")
