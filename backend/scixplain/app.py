import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scixplain.communicator import AsyncCommunicator as Communicator
from scixplain.datasources.wiki import AsyncWikiSearch as WikiSearch
from scixplain.datasources.web import AsyncWebSearch as WebSearch
from scixplain.datasources.arxiv import ArxivSearch
from scixplain.models import QuestionRequest, QuestionResponse, ResourceUsed, ResourceTypes

from uuid import uuid4

# Create an instance of the FastAPI class
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the 'ask' route
@app.post("/ask", response_model=QuestionResponse)
async def ask(request: QuestionRequest) -> QuestionResponse:
    datasources = [
        WikiSearch(
            question=request.question,
            n_pages=request.config.n_pages,
            n_sections=request.config.n_sections,
        ),
        WebSearch(question=request.question, n_articles=request.config.n_pages),
        ArxivSearch(
            question=request.question,
            n_pages=request.config.n_pages,
        ),
    ]

    communicator = Communicator(
        initial_question=request.question,
        age=request.age,
        experience=request.experience,
        datasources=datasources,
    )

    await communicator.run()

    last_message = communicator.messages[-1]

    if type(last_message) == dict:
        content = json.loads(communicator.messages[-1]["content"])
    else:
        content = json.loads(communicator.messages[-1].content)

    resources = []

    for datasource in datasources:
        if type(datasource) == WikiSearch:
            resources.extend(
                [
                    ResourceUsed(
                        url=page.url,
                        sections=page.sections,
                        references=page.references,
                        type=ResourceTypes.WIKIPEDIA,
                    )
                    for page in datasource.pages
                ]
            )
        elif type(datasource) == ArxivSearch:
            resources.extend(
                [
                    ResourceUsed(
                        url=paper.title,
                        sections=paper.categories,
                        references=[link.href for link in paper.links],
                        type=ResourceTypes.ARXIV,
                    )
                    for paper in datasource.papers
                ]
            )

    return QuestionResponse(
        markdown=content["markdown"], references=content["refs_used"], resources=resources
    )


@app.post("/test", response_model=QuestionResponse)
def test(request: QuestionRequest) -> QuestionResponse:
    print(request)
    return QuestionResponse(
        markdown=f"# Success!!! \n\n markdown as be updated!!! \n\n ### TestID \n\n {uuid4()}",
        resources=[
            ResourceUsed(
                url="https://google/com",
                sections=["only one"],
                references=["https://bing.com"],
                type=ResourceTypes.WIKIPEDIA,
            )
        ],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)
