"""Utility functions for MongoDB database operations."""

from pathlib import Path

from bson.json_util import loads
from pymongo.collection import Collection


def reset(collection: Collection) -> None:
    """
    Drop and repopulate a MongoDB collection from the local JSON file.

    Parameters
    ----------
    collection : Collection
        The MongoDB collection to reset.
    """
    data_path = Path(__file__).resolve().parent.parent / "data" / "ds-applicants.json"
    with open(data_path, "r") as f:
        docs = loads(f.read())

    collection.drop()
    collection.insert_many(docs)
