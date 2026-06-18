from __future__ import annotations
from datetime import datetime, UTC
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
import uuid

class Gender(str, Enum):
    MALE = 'male'
    FEMALE = 'female'
    NON_BINARY = 'non_binary'
    OTHER = 'other'
    PREFERE_NOT_TO_SAY = 'prefer_not_to_say'

class Orientation(str, Enum):
    HETEROSEXUAL = 'heterosexual'
    HOMOSEXUAL = "homosexual"
    BISEXUAL = "bisexual"
    PANSEXUAL = "pansexual"
    ASEXUAL = "asexual"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class RelationshipGoals(str, Enum):
    CASUAL = "Casual"
    FRIENDSHIP = "Friendship"
    LONG_TERM = "Long Term"
    MARRIAGE = "Marriage"
    OTHER = "Other"

class Interests(str, Enum):
    # sports
    SPORTS = "sports"
    RUNNING = "running"
    HIKING = "hiking"
    SURFING = "surfing"
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    SAILING = "sailing"
    YOGA = "yoga"
    PILATES = "pilates"
    VOLLEYBALL = "volleyball"
    SKIING = "skiing"
    SNOWBOADING = "snowboading"

    #artystyczne
    MUSIC = "music"
    MOVIES = "movies"
    THEATER = "theater"
    ART = "art"
    PHOTOGRAPHY = "photography"
    DANCING = "dancing"
    LITERATURE = "literature"
    POETRY = "poetry"

    # Technologia & gry
    GAMING = "gaming"
    PROGRAMMING = "programming"
    TECH = "tech"
    BOARD_GAMES = "board_games"

    # Natura & podróże
    TRAVEL = "travel"
    NATURE = "nature"
    GARDENING = "gardening"
    ANIMALS = "animals"

    # Gotowanie & lifestyle
    COOKING = "cooking"
    BAKING = "baking"
    WINE = "wine"
    COFFEE = "coffee"
    VEGANISM = "veganism"

    # Nauka & rozwój
    SCIENCE = "science"
    PSYCHOLOGY = "psychology"
    PHILOSOPHY = "philosophy"
    LANGUAGES = "languages"
    MEDITATION = "meditation"

    # Społeczność
    VOLUNTEERING = "volunteering"
    POLITICS = "politics"
    SPIRITUALITY = "spirituality"

class Photo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    is_main: bool = False
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """
    Profil widoczny dla ewentualnych dopasowań.
    """
    bio: Optional[str] = Field(None, max_length=500, description="Wpisz swoje bio.")
    interests: List[Interests] = Field(default_factory=list, max_length=15)
    photo: List[Photo] = Field(default_factory=list, max_length=6)
    relationship_goals: List[RelationshipGoals] = None
    height_cm: Optional[int] = Field(None, ge=120, le=250, description="Wpisz wzrost w cm.")
    city: Optional[str] = Field(None, max_length=100)
    country: str = Field(default="Polska", max_length=100)

    @field_validator("interests")
    @classmethod
    def max_interests(cls, v: list) -> list:
        if len(v) >15:
            raise ValueError("Można wybrać maksymalnie 15 zainteresowań.")
        return v

    @property
    def main_photo(self) -> Optional[Photo]:
        main = [p for p in self.photo if p.is_main]
        return main[0] if main else (self.photo[0] if self.photo else None)

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """
    Główny model użytkownika łączący dane konta z profilem.
    """
    id: str = Field(default_factory = lambda: str(uuid.uuid4()))
    first_name: str = Field(..., min_length = 1, max_length = 100)
    last_name: str = Field(..., min_length = 1, max_length = 100)
    email: EmailStr
    date_of_birth: date
    gender: Gender
    orientation: Orientation
    profile: UserProfile = Field(default_factory = UserProfile)

    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory = datetime.utcnow)
    last_seen: Optional[datetime] = None

    @property
    def age(self) -> int:
        today = date.today()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @field_validator("date_of_birth")
    @classmethod
    def must_be_an_adult(cls, v: date):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Użytkownik musi mieć conajmniej 18 lat.")
        if age > 110:
            raise ValueError("Została podana nieprawidłowa data urodzenia.")
        return v



