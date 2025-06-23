import random

from pydantic import BaseModel, Field


class Location(BaseModel):
    x: int = Field(..., description="x-coordinate")
    y: int = Field(..., description="y-coordinate")

    def distance_to(self, other: "Location") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Location):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    @classmethod
    def create(cls, x: int, y: int) -> "Location":
        if not 0 < x < 11:
            raise ValueError("Invalid x-coordinate")
        if not 0 < y < 11:
            raise ValueError("Invalid y-coordinate")
        return cls(x=x, y=y)

    @classmethod
    def create_random(cls) -> "Location":
        return cls.create(random.randint(1, 10), random.randint(1, 10))

    model_config = {"frozen": True}
