import logging
import json
import logging.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ada.communicator import AsyncCommunicator as Communicator
from ada.datasources.ds_engines import DatasourceEngines
from ada.models import QuestionRequest, QuestionResponse, Reference, GPTArticleResponse

from uuid import uuid4

# Setup logger
logging.config.fileConfig("./ada/logging.conf", disable_existing_loggers=False)
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
        datasources=[ds.engine for ds in request.config.datasources],
    )

    article = await communicator.ask(question=request.question)

    refs = []

    for ref in communicator.refs_used:
        refs.append(Reference(name=ref["title"], link=ref["link"], type=ref["type"]))

    response = QuestionResponse(article=article, references=refs)
    logger.info(response.model_dump_json())
    return response


@app.post("/test", response_model=QuestionResponse)
def test(request: QuestionRequest) -> QuestionResponse:
    response = json.load(open("./test.json", "r"))
    return QuestionResponse(**response)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)
