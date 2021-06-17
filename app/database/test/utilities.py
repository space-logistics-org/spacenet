import random
from typing import Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DB_URL = "sqlite:///./test.db"

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def with_type(d: Dict, kind) -> Dict:
    return {**d, "type": kind}


def make_subset(d: Dict) -> Dict:
    ret = d.copy()
    for field in d:
        if random.random() < 0.25:
            del ret[field]
    return ret


def first_subset_second(first: Dict, second: Dict) -> bool:
    """
    Return true if first is a subset of second, false otherwise

    :param first: first dict
    :param second: second dict
    :return: true if all elements in first are in second,
             and are mapped to same value, else false
    """
    return all(k in second and first[k] == second[k] for k in first)


def filter_val_not_none(d: Dict) -> Dict:
    return {k: v for k, v in d.items() if v is not None}