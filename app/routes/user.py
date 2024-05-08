from fastapi import APIRouter
from app.db.database import conn 
from schema import serializeDict, serializeList
from bson import ObjectId
from user import User

router = APIRouter() 

@router.get('/')
async def find_all_users():
    return serializeList(conn.local.user.find())

@router.get('/{id}')
async def find_one_user(id):
    return serializeDict(conn.local.user.find_one({"_id":ObjectId(id)}))

@router.post('/')
async def create_user(user: User):
    conn.local.user.insert_one(dict(user))
    return serializeList(conn.local.user.find())

@router.put('/{id}')
async def update_user(id,user: User):
    conn.local.user.find_one_and_update({"_id":ObjectId(id)},{
        "$set":dict(user)
    })
    return serializeDict(conn.local.user.find_one({"_id":ObjectId(id)}))

@router.delete('/{id}')
async def delete_user(id,user: User):
    return serializeDict(conn.local.user.find_one_and_delete({"_id":ObjectId(id)}))