from datetime import timedelta

from hypothesis import strategies as st

__all__ = [
    "VALID_PRIORITIES",
    "VALID_MISSION_TIMES",
    "INVALID_PRIORITIES",
    "INVALID_MISSION_TIMES",
    "EVENT_VALID_MAP",
    "EVENT_INVALID_MAP",
]
VALID_PRIORITIES = st.integers(min_value=1, max_value=5)
VALID_MISSION_TIMES = st.timedeltas(min_value=timedelta(0))
INVALID_PRIORITIES = st.one_of(st.integers(max_value=0), st.integers(min_value=6))
INVALID_MISSION_TIMES = st.timedeltas(max_value=timedelta(milliseconds=-1))
# todo: technically we should include all floats less than 0 here


EVENT_VALID_MAP = {"priority": VALID_PRIORITIES, "mission_time": VALID_MISSION_TIMES}

EVENT_INVALID_MAP = {
    "priority": INVALID_PRIORITIES,
    "mission_time": INVALID_MISSION_TIMES,
}
