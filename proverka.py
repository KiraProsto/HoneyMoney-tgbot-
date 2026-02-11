import math

money1 = 1000
money = 1000
bees = 0
spent = 0

base = 30
scale = 0.3

while True:
    price = base * math.log(bees * scale + 1)
    price = round(price)

    if bees > 0 and bees % 8 == 0:
        n = bees // 8
        price += 80 * n

    if money < price:
        break

    bees += 1
    money -= price
    spent += price
    print()

print("денег было:", money1)
print("потрачено: ", spent)
print("денег осталось:", money)
print()
print("пчел: ", bees)
print()
print("прибыль за день: ", bees * 0.5)
print("прибыль за неделю: ", bees * 0.5 * 7)
print("прибыль в месяц: ", bees * 0.5 * 30)
print()
print("срок окупаемости (месяца):", money1 // (bees * 0.5 * 30))
