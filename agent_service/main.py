import asyncio
from agent_service.graph.builder import build_pipeline
from agent_service.graph.state import PipelineState
from backend.database import SessionLocal
from backend.models import NewsURL
from backend.models.project_results import ProjectResult
from backend.crud import save_pipeline_result


async def run_pipeline_for_all(url_list: list[str]):
    pipeline = build_pipeline()
    results = []

    for idx, url in enumerate(url_list, start=1):
        print(f"\n{'='*50}")
        print(f"[{idx}/{len(url_list)}] 处理: {url}")

        init_state: PipelineState = {
            "current_url": url,
            "html_title": "",
            "html_content": "",
            "is_relevant": False,
            "project_detail": {},
            "search_prompt": "",
            "search_result": {},
            "downloaded_pdf": {},
            "logs": [],
        }

        final_state = await pipeline.ainvoke(init_state)
        save_pipeline_result(url, final_state)

        for log in final_state["logs"]:
            print(f"  {log}")

        if final_state.get("downloaded_pdf"):
            results.append({
                "url": url,
                "detail": final_state["project_detail"],
                "pdf": final_state["downloaded_pdf"],
            })

    print(f"\n全部完成！共处理 {len(url_list)} 条，成功下载 {len(results)} 个 PDF")
    return results


async def main():
    db = SessionLocal()
    try:
        urls = [
            row.url for row in db.query(NewsURL.url)
            .filter(NewsURL.is_relevant == None)  # noqa: E711
            .all()
        ]
    finally:
        db.close()

    print(f"共 {len(urls)} 条待处理 URL")
    await run_pipeline_for_all(urls)


if __name__ == "__main__":
    # 可选：生成 pipeline 图
    try:
        pipeline = build_pipeline()
        image_data = pipeline.get_graph().draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(image_data)
        print("Graph 图已保存为 graph.png")
    except Exception as e:
        print(f"生成图失败: {e}")

    asyncio.run(main())
