from datetime import datetime
import os
from fastapi import FastAPI, Request, Body, HTTPException, status, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional, List
import motor.motor_asyncio

app = FastAPI(docs_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
templates = Jinja2Templates(directory="templates/")
db = client.shorturls

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ShortUrlModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    short_url_id: str = Field(...)
    original_url: str = Field(...)
    password: str = Field(...)
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "short_url_id": "volleyball",
                "original_url": "https://some-very-long-url.com/",
                "password": "some-password",
            }
        }


class UpdateShortUrlModel(BaseModel):
    short_url_id: Optional[str]
    original_url: Optional[str]
    password: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "short_url_id": "volleyball",  # Resulting 
                "original_url": "https://some-very-long-url.com/",
                "password": "some-password",
            }
        }


# @app.post("/", response_description="Add new short URL", response_model=ShortUrlModel)
# async def create_shorturl(shorturl: ShortUrlModel = Body(...)):
#     shorturl = jsonable_encoder(shorturl)
#     new_shorturl = await db["shorturls"].insert_one(shorturl)
#     created_shorturl = await db["shorturls"].find_one({"_id": new_shorturl.inserted_id})
#     return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_shorturl)


# @app.get(
#     "/", response_description="Process a short URL", response_model=List[ShortUrlModel]
# )
# async def list_shorturls():
#     shorturls = await db["shorturls"].find().to_list(1000)
#     return shorturls


@app.get(
    "/{short_url_id}", response_description="List all short URLs",
)
async def list_shorturls(request: Request, short_url_id: str):
    shorturl = await db["shorturls"].find_one({"short_url_id": short_url_id})
    if not shorturl:
        raise HTTPException(status_code=404, detail=f"Short URL {short_url_id} not found")
    if shorturl["password"]:
        return templates.TemplateResponse('form.html', context={"request": request})
    else:
        return RedirectResponse(shorturl["original_url"], status_code=301)


@app.post(
    "/{short_url_id}", response_description="List all short URLs",
)
async def protected_short_url(request: Request, short_url_id: str, password: str = Form(None)):
    if not password:
        return templates.TemplateResponse('form.html', context={"request": request, "error": "Missing password"})

    shorturl = await db["shorturls"].find_one({"short_url_id": short_url_id})
    if not shorturl:
        raise HTTPException(status_code=404, detail=f"Short URL {short_url_id} not found")

    if password == shorturl["password"]:
        return RedirectResponse(shorturl["original_url"], status_code=301)
    return templates.TemplateResponse('form.html', context={"request": request, "error": "Wrong password"})


# @app.get(
#     "/url/{id}", response_description="Get a single short URL", response_model=ShortUrlModel
# )
# async def show_shorturl(id: str):
#     if (shorturl := await db["shorturls"].find_one({"_id": id})) is not None:
#         return shorturl

#     raise HTTPException(status_code=404, detail=f"short url {id} not found")


# @app.put("/{id}", response_description="Update a short URL", response_model=ShortUrlModel)
# async def update_shorturl(id: str, shorturl: UpdateShortUrlModel = Body(...)):
#     shorturl = {k: v for k, v in shorturl.dict().items() if v is not None}

#     if len(shorturl) >= 1:
#         update_result = await db["shorturls"].update_one({"_id": id}, {"$set": shorturl})

#         if update_result.modified_count == 1:
#             if (
#                 updated_shorturl := await db["shorturls"].find_one({"_id": id})
#             ) is not None:
#                 return updated_shorturl

#     if (existing_shorturl := await db["shorturls"].find_one({"_id": id})) is not None:
#         return existing_shorturl

#     raise HTTPException(status_code=404, detail=f"Short URL {id} not found")


# @app.delete("/{id}", response_description="Delete a short URL")
# async def delete_shorturl(id: str):
#     delete_result = await db["shorturls"].delete_one({"_id": id})

#     if delete_result.deleted_count == 1:
#         return Response(status_code=status.HTTP_204_NO_CONTENT)

#     raise HTTPException(status_code=404, detail=f"Short URL {id} not found")
