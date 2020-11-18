"""
Map between ISO 3166 country codes and country names.

Usage:
    country_code [Options] <country>

[Options]
    --iso:  Interpret <country> as an ISO code and show the corresponding country.
"""

###############################################################################################################################################################
#
#       Import
#
###############################################################################################################################################################

import argparse
import typing

from country_codes import COUNTRY_CODES


###############################################################################################################################################################
#
#       country_from_iso
#
###############################################################################################################################################################

def country_from_iso(iso: str) -> int:
    if (country := COUNTRY_CODES.country_from_iso(iso)) is None:
        print(f"Unknown country ISO: {iso}")
        return -1        
    print(f"{iso}: {country}")
    return 0


###############################################################################################################################################################
#
#       iso_from_country
#
###############################################################################################################################################################

def iso_from_country(country: str) -> int:
    if (country_match := COUNTRY_CODES.match_country(country)) is None:
        print(f"Unknown country: {country}")
        return -1
    print(country_match)
    print(f"{country_match}: {COUNTRY_CODES.iso_from_country(country_match)}")
    return 0


###############################################################################################################################################################
#
#       __main__
#
###############################################################################################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iso", action="store_true", help="Interpret the argument as an ISO and show the corresponding country.")
    parser.add_argument("query", type=str, help="The ISO country code or name of the country to convert.")
    args = parser.parse_args()   
    exit(country_from_iso(args.query) if args.iso else iso_from_country(args.query))
