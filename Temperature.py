Temperature = float(input("Enter you Temperature in Celsius: "))

if Temperature < 32:
    print("It's freezing!")
elif Temperature < 50:
    print("It's cold!")
elif Temperature < 70:
    print("It's cool!")
elif Temperature < 90:
    print("It's warm!")
else:
    print("It's hot!")
