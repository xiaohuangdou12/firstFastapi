from datetime import datetime

from fastapi import FastAPI, Path, Query, Request, HTTPException, Depends
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}



# @app.get("/book/{book_id}")
# async def get_book(book_id: int = Path(..., gt=0, lt=100)):
#     return {"message": f"Book ID: {book_id}"}
#
#
#
# @app.get("/author/{name}")
# async def get_author(name: str = Path(..., min_length=2, max_length=50, description="作者的名字")):
#     return {"message": f"Author: {name}"}


# @app.get("/news/news_list")
# async def get_news_list(skip: int = Query(ge=0, le=100, description="跳过的新闻数量"), limit: int = 10):
#     return {"message": f"skip: {skip}, limit: {limit}"}

# class User(BaseModel):
#     username: str = Field(..., min_length=2, max_length=50, description="用户名")
#     password: str = Field(..., min_length=6, max_length=20, description="密码")
#
# @app.post("/register")
# async def register(request: Request, user: User):
#     body_data = await request.json()
#     print(body_data)
#     username = user.username
#     return {"message": f"注册用户: {username}"}
#
# @app.get('/file')
# def get_file():
#     return FileResponse('cs.docx')


class News(BaseModel):
    id: int
    title: str = Field(..., min_length=2, max_length=50, description="新闻标题")
    content: str
    data: dict



@app.middleware("http")
async def middleware1(request: Request, call_next):
    print('request 1')
    response = await call_next(request)
    print('response 1')
    return response

@app.middleware("http")
async def middleware2(request: Request, call_next):
    print('request 2')
    response = await call_next(request)
    print('response 2')
    return response


# @app.get('/news/{news_id}', response_model=News)
# def get_news(news_id: int):
#     return {'id': news_id, 'title': '新df', 'content': '新闻内容'}
#
#
#
# @app.get('/books/{book_id}')
# def get_book(book_id: int):
#     book_list = list(range(1, 6))
#     if book_id not in book_list:
#         raise HTTPException(status_code=404, detail="Book not found")
#     return {'id': book_id, 'title': '新df', 'content': '新闻内容'}





# def common_param():
#     skip: int = Query(default=0, description="跳过的新闻数量")
#     limit: int = Query(default=10)
#     return {'skip': skip, 'limit': limit}
#
# @app.get('/cite')
# def get_news_list(commons = Depends(common_param)):  # Use model type hint
#     return commons


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func, String, select, text

# MySQL连接URL格式：mysql+pymysql://用户名:密码@主机:端口/数据库名
# 从环境变量读取是更好的实践，这里为了示例直接写
DATABASE_URL = "mysql+aiomysql://root:123456@1.116.112.150:3308/fastapi_db"

# 创建数据库引擎
# echo=True会打印SQL语句，方便调试；生产环境建议关闭
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)

class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Book(Base):
    __tablename__ = 'books'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(default=0.0)
    publisher: Mapped[str] = mapped_column(String(255))


async def create_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def startup_event():
    await create_table()



AsyncSession = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async  def get_database():
    async with AsyncSession() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

@app.get('/books')
async def get_books(db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Book).offset(3).limit(2))
    price = result.scalars().all()
    return price


class BookCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=50, description="新闻标题")
    content: str
    price: float = Field(..., gt=0, description="图书价格")
    publisher: str = Field(..., min_length=2, max_length=50, description="出版社")



@app.post("/add_book")
async def add_book(db: AsyncSession = Depends(get_database)):
    # new_book = Book(**book.__dict__)
    # db.add(new_book)
    sql = text("""INSERT INTO `books` (`title`, `content`, `price`, `publisher`) 
VALUES (
    '深入理解MySQL',
    '本书详细讲解MySQL数据库架构、优化技巧与实战案例',
    89.00,
    '电子工业出版社'
);""")
    await db.execute(sql)
    await db.commit()
    return {"message": "Book added successfully"}

print("cs")
print("cs2")
print("cs3")

# @app.post('/books')
# async def create_book(book: Book, db: AsyncSession = Depends(get_database)):
#     async with db as session:
#         session.add(book)
#         await session.commit()
#         return book












