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

try:
    from fuzzywuzzy.process import extractOne
except ImportError:
    logging.warning("Approximate country name matching not available. To enable it: pip install fuzzywuzzy")
    def extractOne(_1, _2, score_cutoff):
        return None


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
    JSON_COUNTRY_CODE   = "Code"
    JSON_COUNTRY_NAME   = "Name"
    JSON_COUNTRY_ALIAS  = "Alias"

    @cached_property
    def data_file(self) -> Path:
        """ Location of the file containing json formatted country code data. """
        return SCRIPT_DIR/"iso_3166_country_codes.json"

    @cached_property
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
        country_to_iso_map = {}
        for item in self.json_data:
            country_name = item[self.JSON_COUNTRY_NAME]
            country_code = item[self.JSON_COUNTRY_CODE]
            country_to_iso_map[country_name.upper()] = country_code
            if (alias_list := item.get(self.JSON_COUNTRY_ALIAS)) is not None:
                for alias in alias_list:
                    country_to_iso_map[alias.upper()] = country_code
        return country_to_iso_map

    @cached_property
    def countries(self) -> set[str]:
        """ A set containing a list of all known countries and aliases. """
        countries = set()
        for item in self.json_data:
            countries.add(item[self.JSON_COUNTRY_NAME])
            if (alias_list := item.get(self.JSON_COUNTRY_ALIAS)) is not None:
                for alias in alias_list:
                    countries.add(alias)
        return countries

    @cached_property
    def upper_country_map(self) -> typing.Dict[str, str]:
        """ Map of upper case country names to correctly capitalized country names. """
        return {c.upper(): c for c in self.countries}

    @cached_property
    def codes(self) -> set[str]:
        """ A view object containing a set of all known ISO 3166 country codes. """
        return self.iso_to_country_map.keys()

    def country_from_iso(self, iso: str) -> str:
        """ Return the country corresponding to iso. """
        return self.iso_to_country_map.get(iso.upper())

    def iso_from_country(self, country: str) -> str:
        """ Return the 1st ISO for country (there should only ever be one). """
        return self.country_to_iso_map.get(country.upper())

    def match_country(self, country: str, cutoff: int=90) -> str:
        """ Return the best known country match for <country> with confidence better than <cutoff>. """
        if (country_match := self.upper_country_map.get(country.upper())) is not None:
            return country_match
        if (country_match := extractOne(country, self.countries, score_cutoff=cutoff)) is not None:
            return country_match[0]
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
