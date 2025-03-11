from pydantic import BaseModel, ConfigDict


class TelegramIDBase(BaseModel):
    telegram_id: int

    model_config = ConfigDict(from_attributes=True)


class UserSchema(TelegramIDBase):
    username: str | None
    first_name: str | None
    last_name: str | None
    