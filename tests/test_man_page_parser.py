import unittest

from parsers.man_page_parser import parse_man_page


SNMPWALK_MAN_TEXT = """
NAME
       snmpwalk - retrieve a subtree of management values using SNMP GETNEXT
       requests
SYNOPSIS
       snmpwalk [APPLICATION OPTIONS] [COMMON OPTIONS] AGENT [OID]
OPTIONS
       -Cc     Do not check whether the returned OIDs are increasing.  Some
        agents (LaserJets are an example) return OIDs out of order, but
        can complete the walk anyway.
       -CE {OID}
        End the walk at the specified OID, rather than a simple subtree.
       -Ci     Include the given OID in the search range.
       -CI     In fact, the given OID will be retrieved automatically if the
        main subtree walk returns no useable values.
       -Cp     Upon completion of the walk, print the number of variables found.
       -Ct     Upon completion of the walk, print the total wall-clock time.
"""


FFUF_HELP_TEXT = """
Fuzz Faster U Fool - v2.1.0

HTTP OPTIONS:
  -H                  Header "Name: Value", separated by colon. Multiple -H allowed.
  -X                  HTTP method to use
  -b                  Cookie data "NAME1=VALUE1; NAME2=VALUE2"

MATCHER OPTIONS:
  -mc                 Match HTTP status codes, or "all" for everything.
  -ms                 Match HTTP response size.

GENERAL OPTIONS:
  -w wordlist         Wordlist file path.
  -u URL              Target URL.
  -ac                 Automatically calibrate filtering options.
"""


class ParseManPageTests(unittest.TestCase):
    def test_extracts_multi_letter_snmpwalk_options(self) -> None:
        page = parse_man_page(SNMPWALK_MAN_TEXT, query="snmpwalk")

        usages = {option.usage for option in page.options}
        self.assertGreaterEqual(len(page.options), 6)
        self.assertIn("-Cc", usages)
        self.assertIn("-CE {OID}", usages)
        self.assertIn("-Ci", usages)
        self.assertIn("-CI", usages)

        ce_option = next(option for option in page.options if option.usage == "-CE {OID}")
        self.assertEqual(ce_option.argument, "OID")
        self.assertIn("End the walk", ce_option.description)

    def test_falls_back_to_raw_help_text_when_sections_are_missing(self) -> None:
        page = parse_man_page(FFUF_HELP_TEXT, query="ffuf")

        usages = {option.usage for option in page.options}
        self.assertGreaterEqual(len(page.options), 7)
        self.assertIn("-mc", usages)
        self.assertIn("-ms", usages)
        self.assertIn("-w wordlist", usages)
        self.assertIn("-u URL", usages)
        self.assertIn("-ac", usages)

        wordlist_option = next(
            option for option in page.options if option.usage == "-w wordlist"
        )
        self.assertEqual(wordlist_option.argument, "wordlist")
        self.assertIn("Wordlist file path", wordlist_option.description)


if __name__ == "__main__":
    unittest.main()
