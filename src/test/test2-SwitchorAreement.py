from SimilarNeuron import Switch, Agreement, BaseSwitch
from pprint import pprint

class Josn:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

class JsonToPerson(BaseSwitch):
    external: Josn = Josn
    internal: Person = Person

    @classmethod
    def transform(cls, json: Josn) -> Person:
        return Person(json.name, json.age)

class PersonToJson(BaseSwitch):
    external: Person = Person
    internal: Josn = Josn

    @classmethod
    def transform(cls, person: Person) -> Josn:
        return Josn(person.name, person.age)    



TOgo = Agreement(JsonToPerson, PersonToJson, Switch(int, str, lambda x: str(x)))

print(JsonToPerson.internal)
print(JsonToPerson.transformation(Josn(name="John", age=30), judge=True))
print(JsonToPerson.get_agreement())
pprint(TOgo.transformation(Josn(name="John", age=30), Person, judge=True))
pprint(TOgo.transformation(Person(name="John", age=30), Josn, judge=True))


