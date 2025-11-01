import math


class Vector:
    # TODO: Implement constructor
    def __init__(self, *components):
        self.components = []
        for n in components:
            self.components.append(n)
        self.size = len(self.components)

    # TODO: Implement __str__

    # TODO: Implement properties
    @property
    def x(self):
        return self.components[0]

    @property
    def y(self):
        return self.components[1]

    @property
    def z(self):
        return self.components[2]

    # TODO: Implement dot product

    # TODO: Implement norm

    # TODO: Implement normalize

    # TODO: Implement cross product

    def __add__(self, rhs):
        new_vec = []
        for i in range(self.size):
            new_vec.append(self.components[i] + rhs.components[i])
        return Vector(*new_vec)

    # TODO: Implement __sub__ (subtraction)

    # TODO: Implement division (which special function name is the correct one?)

    # TODO: Try vector * scalar and scalar * vector
    # TODO: Implement __mul__ (multiplication)

    # TODO: Implement __neg__ (additive inverse)

    def __eq__(self, rhs):
        if self.size != rhs.size:
            return False
        for i in range(self.size):
            if self.components[i] != rhs.components[i]:
                return False
        return True

    # TODO: Implement __getitem__


if __name__ == "__main__":
    v = Vector(1, 2, 3)
    print("v vector", v)
    print(f"The x value is {v.x}")
    print(f"The y value is {v.y()}")
