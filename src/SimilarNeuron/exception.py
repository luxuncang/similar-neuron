class SimilarNeuronException(Exception):
    
    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        self.reason = reason
    
    def __str__(self) -> str:
        return f"{self.name}: {self.reason}"

class AnnotationEmpty(SimilarNeuronException):
    
    def __init__(self, name: str = 'AnnotationEmpty', reason: str = 'The function signature has no comments.') -> None:
        super().__init__(name, reason)

class TransformError(SimilarNeuronException):

    def __init__(self, name: str = 'TransformError', reason: str = 'Type conversion error, view conversion object.') -> None:
        super().__init__(name, reason)
