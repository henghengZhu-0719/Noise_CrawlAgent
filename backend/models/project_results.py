from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class ProjectResult(Base):
    __tablename__ = "project_results"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    news_url         = Column(String(500), nullable=False)

    # extract_node 提取的字段
    project_name     = Column(String(200))   # 项目名称
    province         = Column(String(50))    # 省
    city             = Column(String(100))   # 市
    category         = Column(String(100))   # 项目类别
    total_investment = Column(String(100))   # 项目总投资额
    noise_investment = Column(String(100))   # 声屏障投资额
    noise_type       = Column(String(200))   # 声屏障结构形式
    noise_quantity   = Column(String(200))   # 声屏障工程量
    eia_unit         = Column(String(200))   # 环评单位
    eia_date         = Column(String(100))   # 环评日期
    eia_url          = Column(String(500))   # 环评链接
    open_date        = Column(String(100))   # 通车时间
    progress         = Column(String(50))    # 项目进度
    builder          = Column(String(200))   # 建设单位
    designer         = Column(String(200))   # 设计院
    contractor       = Column(String(200))   # 施工单位
    remark           = Column(Text)          # 备注

    # download_node 的结果
    eia_news_url     = Column(String(500))   # 受理公告 url
    eia_pdf_url      = Column(String(500))   # 环评 PDF 原始链接
    local_pdf_path   = Column(String(500))   # 本地下载路径

    created_at       = Column(DateTime, default=datetime.utcnow)
