from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, model_validator
import uuid

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    GIF = "gif"
    EMOJI = "emoji"

class MessageStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"

class Message(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """
    Pierwsza wiadomość w ramach rozmowy.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    sender_id: str

    type: MessageType.TEXT
    content: str = Field(..., min_length=1, max_length=2500)
    send_at: datetime = Field(default_factory=datetime.now)
    delivery_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    is_deleted: bool = False

class Conversation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """
    Rozmowa między dwoma użytkownikami powiązana z Matchem.
    Powstaje w momencie pierwszej wiadomości.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    match_id: str

    participant_ids: List[str] = Field(..., min_length=2, max_length=2)
    messages: List[Message] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None

    # Archiwizacja (np. po wzajemnym odmatchowaniu)
    is_archived: bool = False

    @model_validator(mode="after")
    def exactly_two_participants(self) -> "Conversation":
        if len(set(self.participant_ids)) != 2:
            raise ValueError("Rozmowa musi mieć dokładnie 2 różnych uczestników.")
        return self

    def add_message(self, message: Message) -> None:
        """Dodaje wiadomość i aktualizuje timestamp ostatniej aktywności."""
        self.messages.append(message)
        self.last_message_at = message.sent_at

    @property
    def last_message(self) -> Optional[Message]:
        return self.messages[-1] if self.messages else None

    @property
    def unread_count_for(self) -> dict[str, int]:
        """Zwraca słownik {user_id: liczba_nieprzeczytanych}."""
        counts: dict[str, int] = {pid: 0 for pid in self.participant_ids}
        for msg in self.messages:
            if msg.status != MessageStatus.READ and msg.sender_id != msg.sender_id:
                # liczymy nieprzeczytane dla odbiorcy
                recipient = next(
                    (p for p in self.participant_ids if p != msg.sender_id), None
                )
                if recipient:
                    counts[recipient] += 1
        return counts

