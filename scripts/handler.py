from pathlib import Path
from generate_special_schema import createSchemas
from generate_simple_schema import createSimpleSchemas
from generate_simple_schema_jy import createSimpleSchemasJY

if __name__ == "__main__":
    # createSchemas("gemini-3.1-flash-lite", Path.cwd() / "data/zod.jsonl")
    # createSimpleSchemas(
    #     model="gemini-3.1-flash-lite",
    #     path_save=Path.cwd() / "data/zod_simple.jsonl",
    #     path_scenarios=Path.cwd() / "data/scenarios_medium.txt",
    #     type_schema="medium",
    # )
    createSimpleSchemasJY(
        model="gemini-3.1-flash-lite",
        path_save=Path.cwd() / "data/jy_simple.jsonl",
        path_scenarios=Path.cwd() / "data/scenarios_medium.txt",
        type_schema="medium",
    )
