from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str | None = None
    myob_customer_id: str | None = None
    is_admin: bool = False


class UserUpdate(BaseModel):
    full_name: str | None = None
    company_name: str | None = None
    myob_customer_id: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    company_name: str | None
    myob_customer_id: str | None
    is_active: bool
    is_admin: bool

    model_config = {"from_attributes": True}
