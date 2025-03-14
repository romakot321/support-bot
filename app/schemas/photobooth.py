from pydantic import BaseModel
import datetime as dt


class PhotoBoothUserSchema(BaseModel):
    id: int
    name: str
    login: str
    gender: str
    isGodModeEnabled: bool
    startAt: dt.datetime | None = None
    maxPhotos: int
    maxStyles: int
    maxModels: int
    isActiveTariff: bool
    tariffId: int | None = None
    maxUploadPhotos: int
    totalGenerations: int
    totalGenerationsTemplate: int
    totalGenerationsGod: int
    totalModels: int
    availableModels: int
    availableGenerations: int
    createdAt: dt.datetime
    hasSubscription: bool
    subscriptionId: str | None = None


class PhotoBoothResponse(BaseModel):
    error: bool
    message: str
    data: PhotoBoothUserSchema
