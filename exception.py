class SimilarNeuronException(Exception):

    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        self.reason = reason

    def __str__(self) -> str:
        return f"{self.name}: {self.reason}"


class AnnotationEmpty(SimilarNeuronException):

    def __init__(
        self, 
        name: str = 'AnnotationEmpty', 
        reason: str = 'The function signature has no comments.'
        ) -> None:
        super().__init__(name, reason)


class TransformError(SimilarNeuronException):

    def __init__(
        self, 
        name: str = 'TransformError', 
        reason: str = 'Type conversion error, look up `transform` object.'
        ) -> None:
        super().__init__(name, reason)


class SwitchEmptyError(SimilarNeuronException):

    def __init__(
        self, 
        name: str = 'SwitchEmptyError', 
        reason: str = 'This `Switch` object not in Agreement.'
        ) -> None:
        super().__init__(name, reason)

class AssignmentError(SimilarNeuronException):

    def __init__(
        self, 
        name: str = 'AssignmentError', 
        reason: str = 'Relationship assignment error.'
        ) -> None:
        super().__init__(name, reason)

class InterfaceTypeError(SimilarNeuronException):

    def __init__(
        self, 
        name: str = 'InterfaceTypeError', 
        reason: str = 'Interface type error.'
        ) -> None:
        super().__init__(name, reason)

class GranularStateError(SimilarNeuronException):

    def __init__(
        self, 
        name: str = 'GranularStateError', 
        reason: str = 'Granular state error.'
        ) -> None:
        super().__init__(name, reason)