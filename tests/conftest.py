"""Configuration for pytest to automatically collect types.

Thanks to Guilherme Salgado.
"""
from typing import Any, Iterator

import pytest
from pyannotate_runtime import collect_types
from typeguard import typechecked


# pylint: disable=W0613
@typechecked
def pytest_collection_finish(session: Any) -> None:
    """Handle the pytest collection finish hook: configure pyannotate.

    Explicitly delay importing `collect_types` until all tests have been
    collected.  This gives gevent a chance to monkey patch the world
    before importing pyannotate.
    """

    collect_types.init_types_collection()


# pylint: disable=W0613
@pytest.fixture(autouse=True)
@typechecked
def collect_types_fixture() -> Iterator:
    """Performs unknown activity."""

    collect_types.start()
    yield
    collect_types.stop()


# pylint: disable=W0613
@typechecked
def pytest_sessionfinish(session: Any, exitstatus: Any) -> None:
    """Performs unknown activity."""
    collect_types.dump_stats("type_info.json")
