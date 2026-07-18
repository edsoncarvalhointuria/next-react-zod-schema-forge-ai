from pathlib import Path
from generate_simple_schema import createSimpleSchemas
from generate_special_schema import createSchemas
from generate_simple_schema_jy import createSimpleSchemasJY

if __name__ == "__main__":
    # createSchemas("gemma-4-31b-it", Path.cwd() / "data/zod_gemma2.jsonl")
    # createSimpleSchemas(
    #     model="gemma-4-31b-it",
    #     path_save=Path.cwd() / "data/zod_gemma_simple2.jsonl",
    #     path_scenarios=(Path.cwd() / "data/scenarios_simple.txt"),
    #     type_schema="micro",
    # )
    createSimpleSchemasJY(
        model="gemma-4-31b-it",
        path_save=Path.cwd() / "data/jy_gemma_simple2.jsonl",
        path_scenarios=(Path.cwd() / "data/scenarios_simple.txt"),
        type_schema="micro",
    )
