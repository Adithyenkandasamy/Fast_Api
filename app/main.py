from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None
try:
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', 
    password='password', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print(cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
    """))
    print(cursor.fetchall())
    print("Database connection was successful")
except Exception as error:
    print("Connecting to the database failed") 
    print("Error: ", error)
    time.sleep(2)

my_posts = [
    {"title": "title of post 1", "content": "content of post 1", "id": 1},
    {"title": "favorite foods", "content": "I like pizza", "id": 2}
]

def find_post(id: int):
    for p in my_posts:
        if p['id'] == id:
            return p

def find_index_post(id: int):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i
    return None  # Explicitly return None if the post is not found

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/posts")
def get_posts():
    # to get all the tables in the database
    aa=cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';""")
    print(aa,"aaaaaaaaaaaaaaaaaa")
    cursor.execute("""SELECT * FROM  posts """)
    posts = cursor.fetchall()

    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

@app.get("/posts/{id}")
def get_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} was not found")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_index_post(id)
    if index is None:  # Check if the index is None
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} does not exist")

    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

  
@app.put("/posts/{id}")
def update_put(id: int, post: Post):
    index = find_index_post(id)

    if index is None:  # Check if the index is None
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} does not exist")
    
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"data": post_dict}

