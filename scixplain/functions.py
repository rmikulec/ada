WIKI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_wikipedia_section",
            "description": "Gets all content from a Wikipedia Section",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "string",
                        "description": "The name of the Wikipedia Page",
                    },
                    "section": {
                        "type": "string",
                        "description": "The name of the Wikipedia Section",
                    },
                },
                "required": ["page", "section"],
            },
        },
    }
]
