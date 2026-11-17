"""SYNTHETIC fixtures only; no fixture is a measurement of the demonstration."""
import copy
import unittest
from tools.analyze import calculate, metric_geometry

def fixture():
    geometry = {"type":"Polygon","coordinates":[[
        [14.42,50.096],[14.4201,50.096],[14.4201,50.0961],
        [14.42,50.0961],[14.42,50.096]]]}
    feature = {"type":"Feature","geometry":geometry,"properties":{
        "id":"synthetic-sector","source_ids":["synthetic-photo"],
        "area_evidence":"synthetic","density_evidence":"synthetic",
        "uncertainty_evidence":"synthetic","area_uncertainty_fraction":0.1,
        "density_ppm2":[1,2,3]}}
    dataset = {"snapshots":[{"id":"synthetic-snapshot","time":"2026-11-15T15:00:00+01:00",
        "coverage_evidence":"synthetic","coverage_complete":True,"features":[feature]}]}
    assets = [{"id":"synthetic-photo","admitted_for_counting":True,"pixel_review":True,
        "authenticity_evidence":"synthetic","capture_time":"2026-11-15T15:00:00+01:00"}]
    return dataset, assets

class Tests(unittest.TestCase):
    def test_missing_data_is_not_zero(self):
        result = calculate({"snapshots":[]}, [])
        self.assertIsNone(result["event_peak"])
        self.assertIsNone(result["observed_max"])
    def test_area_density_and_bounds(self):
        data, assets = fixture()
        result = calculate(data, assets)
        area = metric_geometry(data["snapshots"][0]["features"][0]["geometry"]).area
        self.assertAlmostEqual(result["observed_max"]["central_scenario"], 2*area)
        self.assertAlmostEqual(result["observed_max"]["low"], 0.9*area)
        self.assertAlmostEqual(result["observed_max"]["high"], 3.3*area)
        self.assertIsNone(result["event_peak"])
    def test_snapshots_are_not_summed(self):
        data, assets = fixture()
        second = copy.deepcopy(data["snapshots"][0])
        second["id"] = "synthetic-second"
        data["snapshots"].append(second)
        result = calculate(data, assets)
        self.assertAlmostEqual(result["observed_max"]["central_scenario"],
            result["snapshots"][0]["counts_low_central_high"][1])
    def test_overlapping_sectors_rejected(self):
        data, assets = fixture()
        second = copy.deepcopy(data["snapshots"][0]["features"][0])
        second["properties"]["id"] = "overlap"
        data["snapshots"][0]["features"].append(second)
        with self.assertRaisesRegex(ValueError, "Overlapping"):
            calculate(data, assets)
    def test_unverified_photo_rejected(self):
        data, assets = fixture()
        assets[0]["admitted_for_counting"] = False
        with self.assertRaisesRegex(ValueError, "Unreviewed"):
            calculate(data, assets)
    def test_wrong_time_rejected(self):
        data, assets = fixture()
        assets[0]["capture_time"] = "2026-11-15T13:00:00+01:00"
        with self.assertRaisesRegex(ValueError, "another time"):
            calculate(data, assets)
    def test_wrong_date_rejected(self):
        data, assets = fixture()
        assets[0]["capture_time"] = "2026-03-21T15:00:00+01:00"
        with self.assertRaisesRegex(ValueError, "Wrong event"):
            calculate(data, assets)
    def test_partial_coverage_not_a_total(self):
        data, assets = fixture()
        data["snapshots"][0]["coverage_complete"] = False
        self.assertIsNone(calculate(data, assets)["observed_max"])
    def test_invalid_geometry_rejected(self):
        data, assets = fixture()
        data["snapshots"][0]["features"][0]["geometry"]["coordinates"] = [[
            [14.42,50.096],[14.4201,50.0961],[14.42,50.0961],
            [14.4201,50.096],[14.42,50.096]]]
        with self.assertRaisesRegex(ValueError, "Invalid"):
            calculate(data, assets)
    def test_nan_rejected(self):
        data, assets = fixture()
        data["snapshots"][0]["features"][0]["properties"]["density_ppm2"][1] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite"):
            calculate(data, assets)

if __name__ == "__main__":
    unittest.main()
