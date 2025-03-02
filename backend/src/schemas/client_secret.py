from pydantic import BaseModel


class ClientSecret(BaseModel):
    client_secret: str
