from abc import ABC, abstractmethod


class AsyncDatasource(ABC):
    @abstractmethod
    async def set_data():
        pass

    @abstractmethod
    def to_openai_tool():
        pass

    @abstractmethod
    def get_data():
        pass


class Datasource(ABC):
    @abstractmethod
    def to_openai_tool():
        pass

    @abstractmethod
    def get_data():
        pass
