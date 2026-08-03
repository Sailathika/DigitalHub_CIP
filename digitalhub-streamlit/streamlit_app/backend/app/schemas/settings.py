from pydantic import BaseModel, Field


class UpdateProfileRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = None
    address: str | None = None
    business_name: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)


class SystemInfoResponse(BaseModel):
    app_name: str
    app_version: str
    environment: str
    database_engine: str
    total_users: int
    total_admins: int
    total_vendors: int
    total_datasets: int
    mlflow_tracking_uri: str
