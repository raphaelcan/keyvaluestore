from typing import Optional

from fastapi import FastAPI, Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from models import Store as _Store
from models import User, Task

app = FastAPI()

Store = _Store()


@app.post("/users", response_model=User)
def create_user(user: User, x_token: Optional[str] = Header(None)):
    if x_token != "super_admin":
        return JSONResponse(content={"msg": "You do not have the permission to access this ressource"}, status_code=403)

    try:
        Store.add_user(user)
        return dict(user)
    except User.UsernameAlreadyExists:
        return JSONResponse(content={"msg": "already_exists"}, status_code=400)
    except User.MaximumLengthKey:
        return JSONResponse(content={"msg": "length of username is higher than max length"}, status_code=400)


@app.patch("/users/{username}", response_model=User)
def modify_user(username: str, user: User, x_token: Optional[str] = Header(None)):
    if x_token != "super_admin":
        return JSONResponse(content={"msg": "You do not have the permission to access this ressource"}, status_code=403)

    try:
        stored_user = Store.get_user(username)
        update_data = user.dict(exclude_unset=True)
        updated_item = stored_user.copy(update=update_data)
        Store._users[username][0] = jsonable_encoder(updated_item)
        return updated_item
    except User.DoesNotExist:
        return JSONResponse(content={"msg": f"user {username} does not exist"}, status_code=404)


@app.delete("/users/{username}")
def delete_user(username: str, x_token: Optional[str] = Header(None)):
    if x_token != "super_admin":
        return JSONResponse(content={"msg": "You do not have the permission to access this ressource"}, status_code=403)
    try:
        Store.delete_user(username)
        return JSONResponse(content={"msg": f"user {username} deleted"}, status_code=200)
    except User.DoesNotExist:
        return JSONResponse(content={"msg": f"user {username} does not exist"}, status_code=404)


@app.get("/users/{username}")
def retrieve_user(username: str, x_token: Optional[str] = Header(None)):
    if x_token != "super_admin":
        return JSONResponse(content={"msg": "You do not have the permission to access this ressource"}, status_code=403)
    try:
        user = Store.get_user(username)
        return JSONResponse(dict(user), status_code=200)
    except User.DoesNotExist:
        return JSONResponse(content={"msg": f"user {username} does not exist"}, status_code=404)


@app.get("/users")
def read_users(x_token: Optional[str] = Header(None)):
    if x_token != "super_admin":
        return JSONResponse(content={"msg": "You do not have the permission to access this ressource"}, status_code=403)
    return Store.get_users()


def get_user(x_token):
    try:
        return Store.get_user(username=x_token)
    except User.DoesNotExist:
        return


@app.post("/tasks")
def create_task(task: Task, x_token: Optional[str] = Header(None)):
    user = get_user(x_token)
    if not user:
        return JSONResponse(content={"msg": "Invalid Token"}, status_code=400)
    try:
        user.add_task(task)
    except User.NoMoreCredits:
        return JSONResponse(content={"msg": "Credits Exhausted"}, status_code=400)
    return task


@app.get("/metrics/{username}")
def my_metrics(username: Optional[str], x_token: Optional[str] = Header(None)):
    if username == "me":
        username = x_token
    elif x_token == "super_admin":
        username = username
    else:
        username = None

    user = get_user(username)
    if not user:
        return JSONResponse(content={"msg": "You do not have the permission to access this ressource"}, status_code=403)

    return {"remaining_credits": user.credits - len(user.get_tasks()), "credits": user.credits}


@app.get("/global_metrics")
def global_metrics(x_token: Optional[str] = Header(None)):
    if x_token != "super_admin":
        return JSONResponse(content={"msg": "You do not have the permission to access this ressource"}, status_code=403)
    else:
        return Store.get_number_of_objects()


@app.get("/top_metrics")
def top_metrics(x_token: Optional[str] = Header(None)):
    if x_token != "super_admin":
        return JSONResponse(content={"msg": "You do not have the permission to access this ressource"}, status_code=403)
    else:
        list_users = list(Store.get_users().values())
        list_users = sorted(list_users, key=lambda x: len(x[1]), reverse=True)
        return [u[0].username for u in list_users[:10]]


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", reload=True)
