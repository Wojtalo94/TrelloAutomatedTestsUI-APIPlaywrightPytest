import os
import time
import random
from faker import Faker
import logging


logger = logging.getLogger(__name__)


def _get_or_create_seed():
    """
    Retrieves TEST_SEED from the environment or generates a new one (timestamp).
    Returns the seed as an integer and logs it (once per call).
    """
    seed_str = os.environ.get("TEST_SEED")
    if not seed_str:
        seed_str = str(int(time.time()))
        os.environ["TEST_SEED"] = seed_str
        logger.info(f"TEST SEED created: {seed_str}")
    else:
        logger.debug(f"TEST SEED found: {seed_str}")
    seed = int(seed_str)
    return seed


def _generator_initialization(seed=None):
    """
    Centralized initialization of generators
    """
    if seed is None:
        seed = _get_or_create_seed()

    # initialization of generators
    Faker.seed(seed)
    faker = Faker()
    rnd = random.Random(seed)
    return seed, rnd, faker


def generate_random_name(seed=None):
    """
    The function logs the generated name and the seed used.
    """
    seed, _, faker = _generator_initialization(seed)
    word = faker.word().capitalize()
    logger.info(f"Generated name: {word} (seed={seed})")
    return word


def generate_random_int(min_value=0, max_value=1000, seed=None):
    """
    Returns a random integer in the range [min_value, max_value].
    """
    _, rnd, _ = _generator_initialization(seed)
    value = rnd.randint(min_value, max_value)
    logger.debug(f"Generated int {value} using seed {seed}")
    return value