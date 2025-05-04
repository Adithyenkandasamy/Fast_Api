import sys
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from sqlalchemy.orm import Session 
from .database import engine, get_db
 
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None
try:
    conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', 
    password='pgadmin', cursor_factory=RealDictCursor)
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



@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()

    return{"data": "sucessfull"} 



@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()

    return {"data": posts}  

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: str, db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * from posts WHERE id = %s """, (str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} was not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit() 
    index = find_index_post(id)
    
    if index is None:  # Check if the index is None
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

  
@app.put("/posts/{id}")
def update_put(id: int, post: Post):
    
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",(post.title,post.content,post.published,str(id)))
        
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} does not exist")
    
  
    return {"data": updated_post}
