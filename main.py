from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel

app= FastAPI()


class Post(BaseModel):
    title: str
    content: str

@app.get("/posts")
def root():
    return {"message": "Welcome to my APi"}

@app.get("/")
def get_posts():
    return {"data":"This is your posts"}

@app.post("/createposts")
def create_posts(new_post: Post):
    print(payload)
    return {"new_post": f"title {payload['title']}, content: {payload['content']}"}
