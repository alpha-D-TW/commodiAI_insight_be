from typing import Dict, List, Optional

from gen_ai.prompts import DATE_RANGE_PARAMS
from gen_ai.util import check_params_available, is_not_empty_array


def query_by_params(dates, tags):
    params = (
        [
            {
                "range": {
                    "start_date": {"lte": dates["end_date"]},
                },
            },
            {
                "range": {
                    "end_date": {"gte": dates["start_date"]},
                },
            },
        ]
        if check_params_available(DATE_RANGE_PARAMS, dates)
        else []
    )
    if is_not_empty_array(tags):
        params.append({
            "terms": {
                "tags": tags,
            }
        })
    return (
        {"bool": {"must": params}}
        if is_not_empty_array(params)
        else None
    )


def query_script(
        query_vector: List[float],
        k: int = 4,
        pre_filter: Optional[Dict] = None,
) -> Dict:
    if not pre_filter:
        pre_filter = {"match_all": {}}

    return {
        "size": k,
        "query": {
            "script_score": {
                "query": pre_filter,
                "script": {
                    "source": "knn_score",
                    "lang": "knn",
                    "params": {
                        "field": "vector_field",
                        "query_value": query_vector,
                        "space_type": "l2",
                    },
                },
            }
        },
    }


def text_mapping(
        dim: int,
) -> Dict:
    """For Approximate k-NN Search, this is the default mapping to create index."""
    return {
        "settings": {"index": {"knn": True, "knn.algo_param.ef_search": 512}},
        "mappings": {
            "properties": {
                "vector_field": {
                    "type": "knn_vector",
                    "dimension": dim,
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "nmslib",
                        "parameters": {"ef_construction": 512, "m": 16},
                    },
                },
                "text": {"type": "text"},
                "start_date": {"type": "date", "format": "yyyy-MM-dd"},
                "end_date": {"type": "date", "format": "yyyy-MM-dd"},
                "file_type": {"type": "keyword"},
                "filename": {"type": "text"},
            },
        },
    }
