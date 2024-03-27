import json


def generate_config(config_file_path: str, schema_path: str):
    """
    This method replace json config file path with the schema string.

    :param config_file_path:
    :param schema_path:
    :return:
    """
    with open(schema_path, "r") as schema_f:
        schema = json.load(schema_f)

        schema_str = json.dumps(schema)
    with open(config_file_path, "r") as config_f:
        config = json.load(config_f)
        config['schema.string'] = str(schema_str)

    with open(config_file_path, "w") as config_f:
        json.dump(config, config_f, indent=2)


if __name__ == "__main__":
    generate_config(
        config_file_path="source-technologists-datagen.json",
        schema_path="technologists-schema.json"
    )
