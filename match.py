from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator,ConfigDict
import uuid

class SwipeAction(str, Enum):
    LIKE = "like"
    DISLIKE = "Dislike"
    SUPER_LIKE = "super_like"

class MatchStatus(str, Enum):
    PENDING = "pending"
    MATCHED = "matched"
    REJECTED = "rejected"
    BLOCKED = "blocked"

class Swipe(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """
    Pojedyncze „przesunięcie" – wyraźna akcja jednego użytkownika wobec drugiego.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_user_id: str
    to_user_id: str
    action: SwipeAction
    created_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def no_self_swipe(self) -> "Swipe":
        if self.from_user_id == self.to_user_id:
            raise ValueError("Użutkownik nie może ocenić włsanego profilu.")
        return self

class Match(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """
    Wzajemne dopasowanie dwóch użytkowników.
    Powstaje automatycznie, gdy oboje użytkownicy wykonali akcję LIKE / SUPER_LIKE wobec siebie.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Zawsze przechowujemy user_id_1 < user_id_2, żeby uniknąć duplikatów

    user_id_1: str
    user_id_2: str
    staus: MatchStatus = MatchStatus.PENDING
    matched_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    converstation_id: Optional[str] = None
    @model_validator(mode="after")
    def order_user_ids(self) -> "Match":
        if self.user_id_1 == self.user_id_2:
            raise ValueError("Match nie może istnieć między tym samym użytkownikiem.")
        if self.user_id_1 > self.user_id_2:
            self.user_id_1, self.user_id_2 = self.user_id_2, self.user_id_1
        return self

    def config_match(self) -> None:
        """Zatwierdza dopasowanie (wywołaj gdy drugi użytkownik też polubi)."""
        self.status = MatchStatus.MATCHED
        self.matched_at = datetime.now()

    def block(self) -> None:
        self.status = MatchStatus.BLOCKED
        


