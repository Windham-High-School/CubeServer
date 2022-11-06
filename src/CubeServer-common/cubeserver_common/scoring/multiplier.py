"""Handles any point multipliers that may apply
"""

from abc import ABC
from enum import unique, Enum
from typing import Any

from cubeserver_common.models.utils.modelutils import Encodable
from cubeserver_common.models.team import TeamLevel

class IndivMultiplier(Encodable, ABC):
    """Describes an individual multiplier factor"""

    def __init__(self, value:float=1.0, amt:Any=0):
        super().__init__()
        self.value = value
        self.amt = amt

    def encode(self) -> dict:
        return {"value": self.value, "amt": self.amt}

    @classmethod
    def decode(cls, value: dict):
        i_m = cls()
        i_m.value = value['value']
        i_m.amt = value['amt']
        return i_m

class CostMultiplier(IndivMultiplier):
    """Describes the multiplier associated with excess monetary spending"""

    def __init__(self, level: TeamLevel, amt_spent: float):
        """Calculates the multiplier based on the amount spent as follows:
            For J.V AND Varsity:
                +0.05 for every $1 less than $20
        """
        super().__init__(
            0.05*(20.00-amt_spent) if (amt_spent < 20.00) else 1.0,
            amt_spent
        )

class MassMultiplier(IndivMultiplier):
    """Describes the multiplier associated with mass"""

    def __init__(self, level: TeamLevel, mass: float):
        """Calculates the multiplier based on the cube mass as follows:
            For J.V:
                +0.05 per gram below 400g
            For Varsity:
                +0.05 per gram below 300g
        """
        baseline = 400 if (level == TeamLevel.JUNIOR_VARSITY) else 300
        super().__init__(
            0.05*(baseline-mass) if (mass < baseline) else 1.0,
            mass
        )

@unique
class VolumeUnit(Enum):
    """Enumerates each bounding cube size used for volume determination
    Enum values represent the cube length, in inches"""
    XS = 2
    S = 3
    M = 4
    L = 5
    XL = 7


class VolumeMultiplier(IndivMultiplier):
    """Describes the multiplier associated with different size profiles"""

    def __init__(self, level: TeamLevel, bounding_box: VolumeUnit):
        """Calculates the multiplier based on the amount spent as follows:
            For Varsity:
                See scoring scheme for more info.
        """
        mult = 1.00 if (level == TeamLevel.JUNIOR_VARSITY) else (
            {
                2: 1.3,
                3: 1.2,
                4: 1.1,
                5: 1.0,
                7: 0.8
            }[bounding_box.value]
        )
        super().__init__(
            mult,
            bounding_box
        )

class Multiplier(Encodable, list[IndivMultiplier]):
    """Describes the total multiplier of a team"""

    def __init__(
        self,
        multipliers: list[IndivMultiplier]
    ):
        super().__init__()
        self.extend(multipliers)

    @property
    def amount(self):
        """Calculates the product multiplier"""
        product = 1.00
        for mult in self:
            product *= mult.value
        return product

    def encode(self) -> dict:
        return {"indivs": self}

    @classmethod
    def decode(cls, value: dict):
        mult = cls(value['indivs'])
        return mult
