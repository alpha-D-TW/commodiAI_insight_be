import json
import os
import re
from datetime import datetime
from typing import Any

from gen_ai.config import is_local_env


def split_s3path(s3path):
    protocol = "http://localstack:4576/" if is_local_env() else "s3://"
    file_matched = re.match(f"^{protocol}([^/]*)/(.*)$", s3path)

    if file_matched:
        return file_matched.group(1), file_matched.group(2)
    return None, None


def load_json_file(file_path):
    with open(file_path, encoding="utf8") as data_json:
        try:
            return json.load(data_json)
        except json.decoder.JSONDecodeError:
            return {}


def load_json(v):
    try:
        return json.loads(v)
    except json.decoder.JSONDecodeError:
        return {}


def is_not_empty_array(arr):
    return isinstance(arr, list) and len(arr) > 0


def is_not_empty_str(v):
    return isinstance(v, str) and len(v.strip()) > 0


def check_params_available(params_arr: list[str], params: Any):
    return isinstance(params, dict) and all(
        key in params and is_not_empty_str(params[key]) for key in params_arr
    )


def build_s3_obj_key(file_name, sheet_name):
    return f"knowledge/csv/{file_name}/{sheet_name}.csv"


def load_single_batch_config(file_name):
    return load_json_file(os.path.join(os.path.dirname(__file__), f"./data_config/{file_name}.json"))


def load_merged_batch_config():
    result = []
    batch_config = load_json_file(
        os.path.join(os.path.dirname(__file__), f"./data_config/batch.json")
    )
    for b in batch_config:
        config = load_json_file(
            os.path.join(os.path.dirname(__file__), f"./data_config/{b}.json")
        )
        result.extend(config)
    return result
