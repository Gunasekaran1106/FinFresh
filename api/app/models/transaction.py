from datetime import datetime, timezone
from typing import Optional, Literal
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict

from app.models.user import PyObjectId


class TransactionDocument(BaseModel):
    """
    Represents a transaction document as stored in MongoDB.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str                              # stored as string (stringified ObjectId)
    type: Literal["income", "expense"]
    category: str
    amount: float
    description: str
    date: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_mongo(self) -> dict:
        """Serialise for insertion into MongoDB. Excludes auto-generated id."""
        return self.model_dump(exclude={"id"}, by_alias=False)

    @classmethod
    def from_mongo(cls, data: dict) -> "TransactionDocument":
        """Deserialise a raw MongoDB document into a TransactionDocument."""
        if data is None:
            return None
        data = dict(data)
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)