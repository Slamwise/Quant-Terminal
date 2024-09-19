from abc import ABC, abstractmethod

class DataSource(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def fetch_data(self):
        pass

    @abstractmethod
    def check_health(self):
        pass

class DataStorage(ABC):
    def __init__(self, name, storage_type):
        self.name = name
        self.storage_type = storage_type  # e.g., 'local', 'cloud'
    
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def check_connectivity(self):
        pass
    
    @abstractmethod
    def get_storage_remaining(self):
        pass

class Strategy(ABC):
    def __init__(self, name, parameters, assets):
        self.name = name
        self.parameters = parameters
        self.assets = assets

    @abstractmethod
    def execute(self, data):
        pass

class Indicator(ABC):
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters

    @abstractmethod
    def calculate(self, data):
        pass

class Model(ABC):
    def __init__(self, name, architecture):
        self.name = name
        self.architecture = architecture

    @abstractmethod
    def train(self, data, labels):
        pass

    @abstractmethod
    def predict(self, data):
        pass

class ExchangeAPI(ABC):
    @abstractmethod
    async def get_order_book(self):
        pass

    @abstractmethod
    async def get_trades(self):
        pass