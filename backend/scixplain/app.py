import json
import logging
import logging.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scixplain.communicator import AsyncCommunicator as Communicator
from scixplain.datasources.ds_engines import DatasourceEngines
from scixplain.models import QuestionRequest, QuestionResponse, ResourceUsed

from uuid import uuid4

# Setup logger
logging.config.fileConfig("./scixplain/logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

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
    communicator = Communicator(
        age=request.age,
        experience=request.experience,
        datasources=[ds_config.type for ds_config in request.config.datasources],
    )

    await communicator.ask(question=request.question)

    last_message = communicator.messages[-1]

    if type(last_message) == dict:
        content = json.loads(communicator.messages[-1]["content"])
    else:
        content = json.loads(communicator.messages[-1].content)

    resources = []

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
                type=DatasourceEngines.WIKI,
            )
        ],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)
