"""
Mapping ISO 3166 country codes to country names.
"""

###############################################################################################################################################################
#
#       Import
#
###############################################################################################################################################################

from pathlib import Path
from functools import cached_property
import json
import logging
import typing

from requests.structures import CaseInsensitiveDict


###############################################################################################################################################################
#
#       Global
#
###############################################################################################################################################################

SCRIPT_DIR = Path(__file__).resolve().parent


###############################################################################################################################################################
#
#       CountryCodes
#
###############################################################################################################################################################

class CountryCodes:
    """ Map ISO 3166 country codes to names. """

    # Indexes into the raw json data.
    JSON_COUNTRY_CODE = "Code"
    JSON_COUNTRY_NAME = "Name"
    JSON_COUNTRY_ALIAS = "Alias"

    @cached_property
    def data_file(self) -> Path:
        """ Location of the file containing json formatted country code data. """
        return SCRIPT_DIR/"iso_3166_country_codes.json"

    @property
    def json_data(self) -> json:
        """ Raw json data from the data file. """
        return json.loads(self.data_file.read_text(encoding="utf-8"))

    @cached_property
    def iso_to_country_map(self) -> typing.Dict[str, str]:
        """ Map of ISO country codes to country names. """
        return {item["Code"]: item["Name"] for item in self.json_data}

    @cached_property
    def country_to_iso_map(self) -> typing.Dict[str, str]:
        """ Map of country names and aliases to ISO country codes. """
        country_to_iso_map = CaseInsensitiveDict()
        for item in self.json_data:
            country_name = item[self.JSON_COUNTRY_NAME]
            country_code = item[self.JSON_COUNTRY_CODE]
            assert country_name not in country_to_iso_map.keys(), f"Duplicate country name: {country_name}"
            country_to_iso_map[country_name] = country_code
            if (alias_list := item.get(self.JSON_COUNTRY_ALIAS)) is not None:
                for alias in alias_list:
                    assert alias not in country_to_iso_map.keys(), f"Duplicate country alias: {alias}"
                    country_to_iso_map[alias] = country_code
        return country_to_iso_map

    @cached_property
    def countries(self) -> set[str]:
        """ A view object containing a list of all known countries and aliases. """
        return self.country_to_iso_map.keys()

    @cached_property
    def upper_country_map(self) -> typing.Dict[str, str]:
        """ Map of upper case country names to correctly capitalized country names. """
        return {c.upper(): c for c in self.countries}

    @cached_property
    def codes(self) -> set[str]:
        """ A view object containing a list of all known ISO 3166 country codes. """
        return self.iso_to_country_map.keys()

    def country_from_iso(self, iso: str) -> str:
        """ Return the country corresponding to iso. """
        return self.iso_to_country_map.get(iso.upper())

    def iso_from_country(self, country: str) -> str:
        """ Return the 1st ISO for country (there should only ever be one). """
        return self.country_to_iso_map.get(country)

    def match_country(self, country: str, cutoff: int=90) -> str:
        """ Return the best known country match for <country> with confidence better than <cutoff>. """
        if (country_match := self.upper_country_map.get(country.upper())) is not None:
            return country_match
        try:
            from fuzzywuzzy import process
            if (country_match := process.extractOne(country, self.countries, score_cutoff=cutoff)) is not None:
                return country_match[0]
        except ImportError:
            logging.warning("Approximate country name matching not available. To enable it: pip install fuzzywuzzy")
        return None

    def __getitem__(self, iso: str) -> str:
        return self.country_from_iso(iso)

    def __getattr__(self, iso: str) -> str:
        if (country := self.country_from_iso(iso)) is None:
            raise AttributeError(f"Country code '{iso}' not defined in ISO-3166.")
        return country


###############################################################################################################################################################
#
#       COUNTRY_CODES
#
###############################################################################################################################################################

COUNTRY_CODES = CountryCodes()
