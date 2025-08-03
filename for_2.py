for num in range(1,11):
    print(num)


for number in range(2,20,2):
    print(number)


numbers = [5, 10, 15, 20]

for _num in numbers:
    print(_num + 1)


names = ["Aylin", "John", "Mehdi"]

for name in names:
    print(f"Nice to meet you {name}")


for n in range(1,21):
    if n % 3 == 0:
      print(n)

prices = [100, 200, 300]

for price in prices:
    print(price -(price * 1/10))

Names = ["Ali", "Leyla", "Tom"]

for Name in Names:
    print(f"{Name} --> {len(Name)}")

for square in range(1, 6):
    print(square **2)

words = ["Python", "is", "awesome"]

for word in words:
    print(word, end=' ')


count = 0
for odd in range(1,21):
    if not odd % 2 == 0:
     print(odd)
     count += 1
print(f"Number of odds is {count}")

count_of_days = 0
temperatures = [22, 19, 25, 21, 23]

for temperature in temperatures:
    if temperature > 22:
        print(temperature)
        count_of_days += 1
print(f"Number of days warmer than 22c is {count_of_days}")


cities = ["Baku", "Paris", "London"]

for city in cities:
    print(f"{city} has {len(city)} letters.")


for number in range(1,11):
    print("Number:", number)


scores = [80, 45, 60, 90, 30]

for score in scores:
    logic = "passed" if score >= 50 else "Failed"
    print(logic)
 




