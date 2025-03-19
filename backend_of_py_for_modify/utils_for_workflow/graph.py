from typing_extensions import TypedDict

class GraphState(TypedDict):
    input: str
    generation: str
    documents: str
    resume: str