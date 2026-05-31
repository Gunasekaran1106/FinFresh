from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class PyObjectId(str):
    """
    Custom type that lets Pydantic accept and serialize MongoDB ObjectIds
    as plain strings. Works with Pydantic v2.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _info=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError(f"Invalid ObjectId: {v!r}")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)


class UserDocument(BaseModel):
    """
    Represents a user document as stored in MongoDB.
    Used internally — never returned directly to the client
    (password_hash must never leave the server).
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    email: str
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_mongo(self) -> dict:
        """
        Serialise for insertion into MongoDB.
        Excludes 'id' (MongoDB will generate _id automatically on insert).
        """
        data = self.model_dump(exclude={"id"}, by_alias=False)
        return data

    @classmethod
    def from_mongo(cls, data: dict) -> "UserDocument":
        """Deserialise a raw MongoDB document into a UserDocument."""
        if data is None:
            return None
        data = dict(data)
        # Motor returns _id as ObjectId — convert for Pydantic
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)