choice = input("Enter choice: \n[1]Addition\n[2]Subtraction\n[3]Multiplication\n[4]Division \nEnter your choice: ")

num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

if choice == "1":
    sum = num1 + num2
    print("The sum is:", sum)
elif choice == "2":
    difference = num1 - num2
    print("The difference is:", difference)
elif choice == "3":
    product = num1 * num2
    print("The product is:", product)
elif choice == "4":
    if num2 != 0:
        quotient = num1 / num2
        print("The quotient is:", quotient)
    else:
        print("Error: Division by zero is not allowed.")
else:
    print("Invalid choice. Please select a valid option.")
