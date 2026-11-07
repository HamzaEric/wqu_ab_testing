"""Experiment module for A/B test simulation."""

from typing import Optional, Union

import pandas as pd
import pymongo

from wqulibs.ab_test.data_model import Cohort
from wqulibs.ab_test.params import (
    cohort_params,
    cohort_params_assignment,
)


class MongoRepository:
    """Thin wrapper around a PyMongo database.

    Parameters
    ----------
    client : pymongo.MongoClient
        MongoDB client instance.
    db : str
        Name of the database.
    """

    def __init__(
        self,
        client: pymongo.MongoClient,
        db: str,
    ) -> None:
        self.client = client
        self.db = self.client[db]

    def create_collection(
        self,
        collection: str,
        overwrite: bool = False,
    ) -> None:
        """Create a collection, optionally dropping first.

        Parameters
        ----------
        collection : str
            Collection name.
        overwrite : bool, optional
            Drop existing collection first, by default
            False.
        """
        names = self.db.list_collection_names()
        if collection not in names:
            self.db.create_collection(collection)
        elif overwrite:
            self.db[collection].drop()
            self.db.create_collection(collection)

    def find(
        self,
        collection: str,
        query: Optional[dict] = None,
    ) -> pymongo.cursor.Cursor:
        """Query documents from a collection.

        Parameters
        ----------
        collection : str
            Collection name.
        query : dict, optional
            MongoDB query filter, by default None.

        Returns
        -------
        pymongo.cursor.Cursor
        """
        return self.db[collection].find(query or {})

    def insert(
        self,
        collection: str,
        records: list,
        return_result: bool = False,
    ) -> Optional[dict]:
        """Insert many documents into a collection.

        Parameters
        ----------
        collection : str
            Collection name.
        records : list
            Iterable of documents.
        return_result : bool, optional
            Return summary dict, by default False.

        Returns
        -------
        dict or None
        """
        r = self.db[collection].insert_many(records)
        if return_result:
            return {
                "acknowledged": r.acknowledged,
                "inserted_count": len(r.inserted_ids),
            }
        return None

    def drop(
        self,
        collection: str,
        query: dict,
        return_result: bool = False,
    ) -> Optional[dict]:
        """Delete documents matching a query.

        Parameters
        ----------
        collection : str
            Collection name.
        query : dict
            MongoDB query filter.
        return_result : bool, optional
            Return summary dict, by default False.

        Returns
        -------
        dict or None
        """
        r = self.db[collection].delete_many(query)
        if return_result:
            return {
                "acknowledged": r.acknowledged,
                "deleted_count": r.deleted_count,
            }
        return None


class Experiment:
    """Generate experimental student data and insert
    into a MongoDB repository.

    Parameters
    ----------
    repo : Union[pymongo.MongoClient, MongoRepository]
        A MongoClient or MongoRepository instance.
    db : str, optional
        Database name, by default ``"wqu-abtest"``.
    collection : str, optional
        Collection name, by default
        ``"ds-applicants"``.
    """

    def __init__(
        self,
        repo: Union[pymongo.MongoClient, "MongoRepository"],
        db: str = "wqu-abtest",
        collection: str = "ds-applicants",
    ) -> None:
        self.collection = collection
        self.db = db
        self._attach_repository(repo, db=db)

    def _attach_repository(
        self,
        repository: Union[pymongo.MongoClient, "MongoRepository"],
        db: str = "wqu-abtest",
    ) -> None:
        """Attach a repository to the experiment.

        Parameters
        ----------
        repository : MongoClient or MongoRepository
            A PyMongo client or a repository object
            with ``create_collection``, ``insert``,
            and ``drop`` methods.
        db : str, optional
            Database name (used when a raw MongoClient
            is passed), by default ``"wqu-abtest"``.

        Raises
        ------
        TypeError
            If the repository type is not supported.
        """
        if isinstance(repository, pymongo.MongoClient):
            self.repo = MongoRepository(repository, db)
        elif hasattr(repository, "create_collection"):
            # Accepts any object with the right interface
            # (e.g. student-built MongoRepository in 7.4)
            self.repo = repository
        else:
            raise TypeError(
                "repo must be a MongoClient or an object"
                " with create_collection/insert/drop"
                " methods."
            )

    def add_cohort_to_repository(self, overwrite: bool = False) -> dict:
        """Add cohort of students to repository.

        Parameters
        ----------
        overwrite : bool, optional
            Whether to overwrite collection if it
            already exists, by default False.

        Returns
        -------
        dict
            Insert result summary.
        """
        self.repo.create_collection(
            collection=self.collection,
            overwrite=overwrite,
        )
        r = self.repo.insert(
            self.collection,
            records=self.cohort.yield_students(),
            return_result=True,
        )
        return r

    def run_experiment(
        self,
        days: int,
        start: Optional[str] = None,
        assignment: bool = False,
    ) -> dict:
        """Run simulated A/B experiment.

        Parameters
        ----------
        days : int
            Number of days to run. More days means
            more students.
        start : str, optional
            Start date as ``"YYYY-MM-DD"``, by default
            now.
        assignment : bool, optional
            Use assignment cohort parameters, by
            default False.

        Returns
        -------
        dict
            Insert result summary.
        """
        if start is None:
            start = pd.Timestamp.now()
        params = cohort_params_assignment if assignment else cohort_params
        self.cohort = Cohort(
            days=days,
            start=start,
            is_experiment=True,
            cohort_params=params,
        )
        return self.add_cohort_to_repository()

    def reset_experiment(self) -> dict:
        """Remove experimental student data from
        repository.

        Returns
        -------
        dict
            Delete result summary.
        """
        return self.repo.drop(
            collection=self.collection,
            query={"inExperiment": {"$exists": True}},
            return_result=True,
        )
