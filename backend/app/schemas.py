from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, StringConstraints, Field

Language = Literal["english", "hindi", "hinglish"]
Version = Literal["P0", "P1", "P2"]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1200)]


class CompareRequest(BaseModel):
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1500)]
    language: Language = "english"


class AnalyzeRequest(CompareRequest):
    prompt_version: Version | None = None


class Explanation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    what_happened: Text
    what_to_do_next: list[Text] = Field(min_length=1, max_length=6)
    analogy: Text | None = None
