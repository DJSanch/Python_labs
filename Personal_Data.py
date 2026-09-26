
color = input("Enter your favorite color: ")

colors = ["red", "green", "blue", "yellow", "orange"]

if color in colors:
    print(f"{color} is a great color!")
else:
    exit(f"{color} is not in the list of favorite colors.")


Name1 = input("Enter your first name: ")
Name2 = input("Enter your last name: ")
School = input("Enter your school: ")
Age = int(input("Enter your age: "))
GWA = float(input("Enter your GWA: "))

print(f"Hello {Name1} {Name2}, you are {Age} years old and you study at {School}. Your GWA is {GWA}. You like the color {color}.")
