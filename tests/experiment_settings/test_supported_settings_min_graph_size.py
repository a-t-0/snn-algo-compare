"""Verifies the Supported_settings object catches invalid min_graph_size
specifications."""
# pylint: disable=R0801
import copy
import unittest

from src.experiment_settings.Supported_settings import Supported_settings
from src.experiment_settings.verify_supported_settings import (
    verify_configuration_settings,
)
from tests.experiment_settings.test_generic_configuration import (
    adap_sets,
    rad_sets,
    supp_sets,
    with_adaptation_with_radiation,
)


class Test_min_graph_size_settings(unittest.TestCase):
    """Tests whether the verify_configuration_settings_types function catches
    invalid min_graph_size settings.."""

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supp_sets = Supported_settings()
        self.valid_min_graph_size = self.supp_sets.min_graph_size

        self.invalid_min_graph_size_value = {
            "min_graph_size": "invalid value of type string iso list of"
            + " floats",
        }

        self.supp_sets = supp_sets
        self.adap_sets = adap_sets
        self.rad_sets = rad_sets
        self.with_adaptation_with_radiation = with_adaptation_with_radiation

    # TODO: write test min_max_graphs is of invalid type.
    def test_catch_invalid_min_graph_size_value_type_too_low(self):
        """."""
        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        # Set negative value of min_graph_size in copy.
        config_settings["min_graph_size"] = -2

        with self.assertRaises(Exception) as context:
            verify_configuration_settings(
                self.supp_sets, config_settings, has_unique_id=False
            )

        self.assertEqual(
            "Error, setting expected to be at least "
            + f"{self.supp_sets.min_graph_size}. "
            + f"Instead, it is:{-2}",
            str(context.exception),
        )

    def test_catch_invalid_min_graph_size_value_type_too_high(self):
        """."""
        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        # Set negative value of min_graph_size in copy.
        config_settings["min_graph_size"] = 50

        with self.assertRaises(Exception) as context:
            verify_configuration_settings(
                self.supp_sets, config_settings, has_unique_id=False
            )

        self.assertEqual(
            "Error, setting expected to be at most "
            + f"{self.supp_sets.max_graph_size}. Instead, it is:"
            + "50",
            str(context.exception),
        )

    def test_catch_empty_min_graph_size_value(self):
        """."""
        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        # Set negative value of min_graph_size in copy.
        config_settings["min_graph_size"] = None

        with self.assertRaises(Exception) as context:
            verify_configuration_settings(
                self.supp_sets, config_settings, has_unique_id=False
            )

        self.assertEqual(
            "Error, expected type:<class 'int'>, yet it was:"
            + f"{type(None)} for:{None}",
            str(context.exception),
        )

    def test_returns_valid_m(self):
        """Verifies a valid min_graph_size is returned."""
        returned_dict = verify_configuration_settings(
            self.supp_sets,
            self.with_adaptation_with_radiation,
            has_unique_id=False,
        )
        self.assertIsInstance(returned_dict, dict)

    def test_empty_min_graph_size(self):
        """Verifies an exception is thrown if an empty min_graph_size dict is
        thrown."""

        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        # Remove key and value of m.

        config_settings.pop("min_graph_size")

        with self.assertRaises(Exception) as context:
            verify_configuration_settings(
                self.supp_sets, config_settings, has_unique_id=False
            )

        self.assertEqual(
            "'min_graph_size'",
            str(context.exception),
        )
