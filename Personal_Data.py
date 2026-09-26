
color = input("Enter your favorite color: ")

if color == "red":
    print("Your favorite color is red!")
elif color == "green":
    print("Your favorite color is green!")
elif color == "blue":
    print("Your favorite color is blue!")
elif color == "yellow":
    print("Your favorite color is yellow!")
elif color == "orange":
    print("Your favorite color is orange!")
else:
    exit("Your favorite color is not in the list of colors.")



Name1 = input("Enter your first name: ")
Name2 = input("Enter your last name: ")
School = input("Enter your school: ")
Age = int(input("Enter your age: "))
GWA = float(input("Enter your GWA: "))

print(f"Hello {Name1} {Name2}, you are {Age} years old and you study at {School}. Your GWA is {GWA}. You like the color {color}.")
