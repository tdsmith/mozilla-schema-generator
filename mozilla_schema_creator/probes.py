from __future__ import annotations

from datetime import datetime
from .schema import Schema
from typing import Any
from .utils import _get

class Probe(object):

    type_key = "type"
    name_key = "name"
    history_key = "history"

    def __init__(self, identifier: str, definition: dict):
        self.id = identifier
        self.type = definition[self.type_key]
        self.name = definition[self.name_key]
        self.definition = definition[self.history_key][0]

    def get_type(self) -> str:
        return self.type

    def get_name(self) -> str:
        return self.name

    def get_first_added(self) -> datetime:
        raise NotImplementedError("First added is not available on generic probe")

    def get_schema(self) -> Schema:
        raise NotImplementedError("Get Schema is not available on generic probe")

    def get(self, *k) -> Any:
        return _get(self.definition, k)

    def __lt__(self, other: Probe) -> bool:
        if self.get_first_added() == other.get_first_added():
            return self.get_name() < other.get_name()

        return self.get_first_added() < other.get_first_added()


class MainProbe(Probe):

    first_added_key = "first_added"

    # TODO: Do we use log_sum_*, sum_squares_*?
    histogram_schema = {
        "type": "object",
        "properties":{
            "bucket_count":{
                "minimum":0,
                "type":"integer"
            },
            "histogram_type":{
                "minimum":0,
                "type":"integer"
            },
            "range":{
                "items":{
                    "type":"integer"
                },
                "type":"array"
            },
            "sum":{
                "minimum":0,
                "type":"integer"
            },
            "values":{
                "additionalProperties": False,
                "patternProperties":{
                    "^[0-9]+$":{
                        "minimum":0,
                        "type":"integer"
                    }
                },
                "type":"object"
            }
        }
    }



    def __init__(self, identifier: str, definition: dict):
        self._set_first_added(definition[self.first_added_key])
        super().__init__(identifier, definition)

    def _set_first_added(self, first_added_value: dict):
        vals = [datetime.fromisoformat(v) for v in first_added_value.values()]
        self.first_added = min(vals)

    def get_first_added(self) -> datetime:
        return self.first_added

    def get_schema(self) -> Schema:
        # Get the schema based on the probe type
        if self.get_type() == "scalar":
            ptype = self.get("details", "kind")
            if ptype == "boolean":
                pschema = {"type": "boolean"}
            elif ptype == "string":
                pschema = {"type": "string"}
            elif ptype == "uint":
                pschema = {"type": "integer"}
            else:
                raise Exception("Unknown scalar type " + ptype)
        elif self.get_type() == "histogram": 
            pschema = self.histogram_schema

        # Add nested level if keyed
        if self.get("details", "keyed"):
            final_schema = {"type": "object", "additionalProperties": pschema}
        else:
            final_schema = pschema

        return Schema(final_schema)