from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict
from portal_randkowy_user import Gender, Orientation, Interests, RelationshipGoals

class AgeRange(BaseModel):
    min_age:int = Field(18, ge=18, le=99)
    max_age:int = Field(99, ge=18, le=99)

    @model_validator(mode="after")
    def min_lte_max(self) -> "AgeRange":
        if self.min_age > self.max_age:
            raise ValueError("Minimalny wiek nie może być większy niż maksymalny.")
        return self

class MatchPreference(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """
    Kryteria, według których chcesz znaleźć partnera.
    """
    user_id: str
    # Kryteria wybory drugiej osoby
    preferred_genders: List[Gender] = Field(
        default_factory=list,
        description = "Preferowane płcie partnerów (pusta lista = brak ograniczenia)"
    )
    preferred_orientations: List[Orientation] = Field(
        default_factory=list,
        description="Preferowane orientacje (pusta lista = brak ograniczenia)"
    )
    # wiek
    age_range: AgeRange = Field(default_factory=AgeRange)

    #zainteresowania
    preferred_interests: List[Interests] = Field(
        default_factory=list,
        max_length=15,
        description="Zainteresowania, na których zależy użytkownikowi u partnera"
    )
    # cel
    relationship_goals: List[RelationshipGoals] = Field(
        default_factory=list,
        description='Akceptowane cele związku (pusta lista = brak ograniczenia)'
    )
    #lokalizcja
    max_distance_km: Optional[int] = Field(
        None, ge=1, le=20_000,
        description="Maksymalna odległość w km (None = brak ograniczenia)"
    )
