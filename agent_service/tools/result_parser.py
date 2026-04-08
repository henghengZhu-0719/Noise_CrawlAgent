import re
import json


def parse_result(msg_content):
    thinking = ""

    if isinstance(msg_content, list):
        text_parts = []
        for block in msg_content:
            if isinstance(block, dict):
                if block.get("type") == "thinking":
                    thinking += block.get("thinking", "") + "\n"
                elif block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            elif isinstance(block, str):
                text_parts.append(block)
        msg_content = "".join(text_parts)
    else:
        msg_content = str(msg_content)

    think_match = re.search(r'<think>(.*?)</think>', msg_content, re.DOTALL)
    if think_match:
        thinking += think_match.group(1).strip()

    text_content = re.sub(r'<think>.*?</think>', '', msg_content, flags=re.DOTALL).strip()

    json_match = re.search(r'\[\s*\{.*?\}\s*\]', text_content, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
    else:
        json_str = re.sub(r'^```(?:json)?\s*', '', text_content)
        json_str = re.sub(r'\s*```$', '', json_str).strip()

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败: {e}\n提取到的字符串为:\n{json_str}")
        data = []

    return thinking.strip(), data
