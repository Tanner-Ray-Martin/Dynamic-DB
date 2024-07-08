from pydantic import BaseModel

this_file_path = __file__


def pydantic_to_sqlalchemy(pydantic_model: BaseModel): ...


def schema_to_pydantic(schema: BaseModel): ...
