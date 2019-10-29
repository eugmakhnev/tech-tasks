"""
Задача о кенгуру
----------------

Есть два кенгуру на оси координат, готовые прыгать в одном направлении (например, в
положительном направлении). Первый кенгуру находится в положении x1 и прыгает на
расстояние v1 за прыжок. Анологично с первым кенгуру, второй находится изначально в
положении x2 и прыгает на v2 за прыжок. По заданным начальным положениям и
скоростям можете ли вы определить окажутся ли они в одном месте в одно и тоже время?

### Входные данные​

Stdin с четырьми целыми числами, разделенными пробелом формата: x1 v1 x2 v2

### Ограничения​

* − 10000 ≤ x1, x2 ≤ 10000
* − 10000 ≤ v1, v2 ≤ 10000

### Формат вывода​

В stdout YES, если кенгуру могут встретится в одном месте в одно и тоже время. И NO в
обратном случае.

### Примеры​

Вход: 0 3 4 2

Результат: YES

Вход: 0 2 5 3

Результат: NO
"""
from lib import will_kangaroos_collide, Kangaroo

if __name__ == '__main__':
    print(will_kangaroos_collide(Kangaroo(8, 2), Kangaroo(5, 3)))
    print(will_kangaroos_collide(Kangaroo(0, 2), Kangaroo(5, 3)))