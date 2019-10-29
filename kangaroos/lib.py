# --- Types ---
class Kangaroo:
    def __init__(self, initial_position: int, step: int):
        self.position = initial_position
        self.step = step

    def jump(self):
        self.position += self.step


# --- Utils ---
def is_one_of_kangaroos_unreachable(first: Kangaroo, second: Kangaroo) -> bool:
    if first.position != second.position:
        favorite, outsider = (first, second) \
            if first.position > second.position else (second, first)

        if favorite.step >= outsider.step:
            return True
    # handle situation with equal positions, but not equal steps
    else:
        if first.step != second.step: return True

    return False


# --- Solution ---
MAX_POSITION = 10000


def will_kangaroos_collide(first: Kangaroo, second: Kangaroo) -> bool:
    while first.position < MAX_POSITION and second.position < MAX_POSITION:
        if first.position == second.position:
            return True

        if is_one_of_kangaroos_unreachable(first, second): break

        first.jump()
        second.jump()

    return False


# --- Tests ---
def test_is_one_of_kangaroos_unreachable():
    # simple
    assert is_one_of_kangaroos_unreachable(Kangaroo(0, 2), Kangaroo(5, 3)) is True

    # position is greater, step is lower
    assert is_one_of_kangaroos_unreachable(Kangaroo(9, 2), Kangaroo(5, 3)) is False

    # equal positions, equal steps
    assert is_one_of_kangaroos_unreachable(Kangaroo(0, 2), Kangaroo(0, 2)) is False

    # equal positions, not equal steps
    assert is_one_of_kangaroos_unreachable(Kangaroo(0, 2), Kangaroo(0, 3)) is True


def test_will_kangaroos_collide():
    # simple success
    assert will_kangaroos_collide(Kangaroo(0, 3), Kangaroo(4, 2)) is True

    # simple failure
    assert will_kangaroos_collide(Kangaroo(0, 2), Kangaroo(5, 3)) is False

    # max position abortion
    assert will_kangaroos_collide(Kangaroo(MAX_POSITION - 1, 10), Kangaroo(MAX_POSITION + 1, 3)) is False
