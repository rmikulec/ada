from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scixplain.communicator import AsyncCommunicator as Communicator
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
    async with Communicator(
        initial_question=request.question,
        age=request.age,
        experience=request.experience,
        n_pages=request.config.n_pages,
        n_sections=request.config.n_sections,
        max_tokens=request.config.max_tokens,
    ) as communicator:
        await communicator.run()

        last_message = communicator.messages[-1]

        if type(last_message) == dict:
            md = communicator.messages[-1]["content"]
        else:
            md = communicator.messages[-1].content

        resources = [
            ResourceUsed(
                url=page.url,
                sections=page.sections,
                references=page.references,
                type=ResourceTypes.WIKIPEDIA,
            )
            for page in communicator.pages
        ]

        print(type(md))
        print(md)

        return QuestionResponse(markdown=md, resources=resources)


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
