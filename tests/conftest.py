# tests/conftest.py
import numpy as np
import pytest
import simpy

from pizzeria_sim.config import PizzeriaConfig
from pizzeria_sim.model import Pizzeria


@pytest.fixture
def default_config():
    return PizzeriaConfig()


@pytest.fixture
def env():
    return simpy.Environment()


@pytest.fixture
def pizzeria(env, default_config):
    np.random.seed(42)  # deterministic runs
    return Pizzeria(env, default_config)
