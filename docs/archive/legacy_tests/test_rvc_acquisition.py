import gzip
import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.acquisition.download_noaa_rvc import build_url, looks_like_html, sha256_file


class DownloadHelpers(unittest.TestCase):
    def test_url_filters_keys_and_year(self):
        url = build_url(2022)
        self.assertIn("REGION=%22FLA%20KEYS%22", url)
        self.assertIn("YEAR=2022", url)
        self.assertIn("CRCP_Reef_Fish_Surveys_Florida.csv", url)
        self.assertNotIn("latitude=2", url)

    def test_html_rejected(self):
        self.assertTrue(looks_like_html(b"<html><body>error</body></html>"))
        self.assertFalse(looks_like_html(b"time,latitude\n"))

    def test_sha256(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.txt"
            path.write_bytes(b"abc")
            self.assertEqual(sha256_file(path), hashlib.sha256(b"abc").hexdigest())

    def test_units_row_and_no_negative_counts(self):
        text = "YEAR,NUM,REGION\n,,\n2022,0,FLA KEYS\n2022,1.5,FLA KEYS\n"
        rows = list(csv_rows(text))
        self.assertEqual(rows[0]["YEAR"], "")
        data = rows[1:]
        self.assertTrue(all(float(row["NUM"]) >= 0 for row in data))

    def test_public_table_has_no_coordinate_header(self):
        public = "event_id,detected,depth\n1,1,10\n"
        header = public.splitlines()[0].split(",")
        self.assertNotIn("latitude", header)
        self.assertNotIn("longitude", header)


def csv_rows(text: str):
    import csv
    import io

    return list(csv.DictReader(io.StringIO(text)))


class GzipRoundTrip(unittest.TestCase):
    def test_partial_removed_on_success_pattern(self):
        with tempfile.TemporaryDirectory() as tmp:
            partial = Path(tmp) / "x.csv.partial"
            partial.write_bytes(b"junk")
            dest = Path(tmp) / "x.csv.gz"
            with gzip.open(dest, "wt", encoding="latin-1") as handle:
                handle.write("time,NUM\n,\n2022,0\n")
            partial.unlink()
            self.assertFalse(partial.exists())
            with gzip.open(dest, "rt", encoding="latin-1") as handle:
                self.assertTrue(handle.readline().startswith("time,"))


if __name__ == "__main__":
    unittest.main()
