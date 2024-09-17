from classes.base import Model
from sklearn.neural_network import MLPClassifier

class NeuralNetworkModel(Model):
    def __init__(self, name, architecture):
        super().__init__(name, architecture)
        self.model = MLPClassifier(**architecture)

    def train(self, data, labels):
        self.model.fit(data, labels)

    def predict(self, data):
        return self.model.predict(data)
