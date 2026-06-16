#response_parser.py
def extract_response_text(message) -> str:
    content = message
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(
                        item.get("text", "")
                    )

        return "\n".join(text_parts)

    return str(content)