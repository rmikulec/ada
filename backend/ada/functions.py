from typing import List


def get_wiki_function(section_titles: List[str]):
    return {
        "type": "function",
        "function": {
            "name": "get_wikipedia_content",
            "description": "Gets content from a wikipedia section, including text, images, and any references used.",
            "parameters": {
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "the 'title/section' of the wikipedia page to get content from.",
                        "enum": section_titles,
                    },
                },
                "required": ["route"],
            },
        },
    }
