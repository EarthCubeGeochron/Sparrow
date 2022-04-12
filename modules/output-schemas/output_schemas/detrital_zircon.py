from enum import Enum
from decimal import Decimal
from typing import List
from .base import Datum, DataModel


class Age(Datum):
    unit = "Myr"


class DecaySystem(str, Enum):
    _207Pb_235U = "207Pb_235U"
    _206Pb_238U = "207Pb_238U"
    _206Pb_207Pb = "206Pb_207Pb"
    _208Pb_232Th = "208Pb_232Th"


class UPbAge(Age):
    system: DecaySystem
    age: Age


class SpectrumAge(DataModel):
    best_age: UPbAge
    concordance: Decimal


class AgeSpectrum(DataModel):
    ages: List[SpectrumAge]


class ConcordiaAge(DataModel):
    age206Pb_238U: Age
    age207Pb_235U: Age
    age206Pb_207Pb: Age

    # We should have a set of transformers
    def calc_best_age(self) -> SpectrumAge:
        # We should do an actual conconrdance calculation here
        return SpectrumAge(
            best_age=self.age206Pb_238U,
            concordance=self.age206Pb_238U.value / self.age206Pb_207Pb.value,
        )


class ConcordiaSpectrum(DataModel):
    ages: List[ConcordiaAge]
