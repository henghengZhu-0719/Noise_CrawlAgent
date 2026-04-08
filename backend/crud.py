from backend.database import SessionLocal
from backend.models import NewsURL, ProjectResult


def save_pipeline_result(url: str, final_state: dict):
    with SessionLocal() as session:
        news_row = session.query(NewsURL).filter(NewsURL.url == url).first()
        if news_row:
            news_row.is_relevant = final_state.get("is_relevant", False)

        if final_state.get("is_relevant"):
            detail = final_state.get("project_detail", {})
            pdf_info = final_state.get("downloaded_pdf", {})
            project = ProjectResult(
                news_url=url,
                project_name=detail.get("项目名称"),
                province=detail.get("省"),
                city=detail.get("市"),
                category=detail.get("项目类别"),
                total_investment=detail.get("项目总投资额(万元)"),
                noise_investment=detail.get("声屏障投资额(万元)"),
                noise_type=detail.get("声屏障结构形式"),
                noise_quantity=detail.get("声屏障工程量"),
                eia_unit=detail.get("环评单位"),
                eia_date=detail.get("环评日期"),
                eia_url=detail.get("环评链接"),
                open_date=detail.get("通车时间"),
                progress=detail.get("项目进度"),
                builder=detail.get("建设单位"),
                designer=detail.get("设计院"),
                contractor=detail.get("施工单位"),
                remark=detail.get("备注"),
                eia_news_url=pdf_info.get("新闻url"),
                eia_pdf_url=pdf_info.get("环评文件url"),
                local_pdf_path=pdf_info.get("环评文件下载路径"),
            )
            session.add(project)

        session.commit()
