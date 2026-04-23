from sqlalchemy import Column, BigInteger, String, Integer, DateTime, SmallInteger, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from backend.database import Base


class NewsURL(Base):
    """
    新闻URL模型

    Attributes:
        id          (BigInteger): 主键ID，自增
        url         (LONGTEXT):   新闻原始URL，唯一且不可为空
        title       (String):     新闻标题，最长255字符
        content     (LONGTEXT):   新闻正文HTML内容
        source      (String):     新闻来源站点，如 "新华网"、"央视新闻"
        publish_date(DateTime):   新闻发布时间（来源站点标注的时间）
        crawl_status(SmallInteger):爬取状态
                                    0 = 待爬取
                                    1 = 爬取成功
                                    2 = 爬取失败
                                    3 = 跳过/忽略
        is_relevant (SmallInteger):相关性标注
                                    NULL = 未处理
                                    0    = 不相关
                                    1    = 相关
        created_at  (DateTime):   记录创建时间，自动填充
        updated_at  (DateTime):   记录最后更新时间，自动更新
    """

    __tablename__ = "news_urls"

    # ── 主键 ──────────────────────────────────────────────
    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="主键ID",
    )

    # ── 核心内容 ──────────────────────────────────────────
    url = Column(
        String(2048),           # LONGTEXT 无法直接建唯一索引，改用 String(2048)
        unique=True,
        nullable=False,
        index=True,
        comment="新闻原始URL",
    )
    title = Column(
        String(512),
        nullable=True,          # 爬取失败时标题可能为空
        comment="新闻标题",
    )
    content = Column(
        LONGTEXT,
        nullable=True,          # 爬取失败时内容可能为空
        comment="新闻正文HTML",
    )

    # ── 来源信息 ──────────────────────────────────────────
    source = Column(
        String(255),
        nullable=True,
        comment="新闻来源，如：新华网、央视新闻",
    )
    publish_date = Column(
        DateTime,
        nullable=True,          # 部分页面可能无法解析发布时间
        comment="新闻发布时间（来源站点）",
    )

    # ── 爬取状态 ──────────────────────────────────────────
    crawl_status = Column(
        SmallInteger,
        nullable=False,
        default=0,
        comment="爬取状态：0=待爬取，1=成功，2=失败，3=跳过",
    )

    # ── 相关性标注 ────────────────────────────────────────
    is_relevant = Column(
        SmallInteger,
        nullable=True,
        default=None,
        comment="相关性：NULL=未处理，0=不相关，1=相关",
    )

    # ── 时间戳 ────────────────────────────────────────────
    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        comment="记录创建时间",
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        comment="记录最后更新时间",
    )

    def __repr__(self) -> str:
        return (
            f"<NewsURL id={self.id} source={self.source!r} "
            f"crawl_status={self.crawl_status} is_relevant={self.is_relevant}>"
        )
