from backend.database import engine, Base
from backend.models import NewsURL, ProjectResult


def init_database():
    Base.metadata.create_all(bind=engine)
    print("数据库表初始化完成")


if __name__ == "__main__":
    init_database()
