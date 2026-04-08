from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from backend.database import Base

class NewsURL(Base):
    """
    新闻URL模型
    :param id: 主键ID
    :param url: 新闻URL
    :param title: 新闻标题
    :param content: 新闻内容
    :param created_at: 创建时间
    :param is_relevant: 0表示不相关，1表示相关，可为空
    """
    __tablename__ = "news_urls"
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="新闻URLID")
    url = Column(LONGTEXT, nullable=False, comment="新闻URL")
    title = Column(String(255), nullable=False, comment="新闻标题")
    content = Column(LONGTEXT, nullable=False, comment="html存的位置")
    created_at = Column(DateTime, nullable=False, default=func.now(), comment="创建时间")
    is_relevant = Column(Integer, nullable=True, comment="是否处理了，None表示未处理，0是不相关，1是相关")


   