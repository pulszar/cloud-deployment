from pydantic import BaseModel

class Note(BaseModel): # Note schema
    message : str
    
class Purchase(BaseModel):
    item : str
    quantity : int
    date_purchased : str
    
# AUTH

class Token(BaseModel):
    access_token: str
    token_type: str
    
class User(BaseModel):
    user_id: int
    username: str
    email: str
    disabled: bool | None = None
    
class UserInDB(User):
    hashed_password: str
    
class TokenData(BaseModel):
    username : str
    id : int
    
class CreateUser(BaseModel):
    username: str
    email: str
    password: str