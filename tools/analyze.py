"""Calculate observed simultaneous occupancy, never attendance summed across time."""
import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform

PROJECT = Transformer.from_crs("EPSG:4326", "EPSG:5514", always_xy=True).transform

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def number(value):
    require(isinstance(value, (int, float)) and not isinstance(value, bool)
        and math.isfinite(value), "Expected finite numeric value")
    return value

def timestamp(value):
    t = datetime.fromisoformat(value)
    require(t.tzinfo is not None, "Capture time requires timezone")
    require(t.astimezone(ZoneInfo("Europe/Prague")).date().isoformat() == "2026-11-15",
        "Wrong event date")
    return t

def metric_geometry(geometry):
    require(geometry.get("type") in ("Polygon", "MultiPolygon"), "Expected polygon")
    g = shape(geometry)
    require(g.is_valid and not g.is_empty, "Invalid or empty polygon")
    x0,y0,x1,y1 = g.bounds
    require(14.35 < x0 <= x1 < 14.5 and 50.07 < y0 <= y1 < 50.13,
        "Geometry must use WGS84 longitude,latitude around Letna")
    result = transform(PROJECT, g)
    require(result.is_valid and result.area > 0, "Invalid metric geometry")
    return result

def calculate(dataset, assets):
    output = {"status":"insufficient_evidence", "event_peak":None,
        "observed_max":None, "snapshots":[], "interval_type":"scenario_envelope_not_confidence_interval"}
    if not dataset.get("snapshots"):
        output["reason"] = "No measured sectors, calibrated densities or synchronized snapshots."
        return output
    registry = {a["id"]:a for a in assets}
    require(len(registry) == len(assets), "Duplicate asset IDs")
    snapshot_ids = set()
    for shot in dataset["snapshots"]:
        require(shot["id"] not in snapshot_ids, "Duplicate snapshot ID")
        snapshot_ids.add(shot["id"])
        t = timestamp(shot["time"])
        skew = number(shot.get("max_skew_seconds", 0))
        require(0 <= skew <= 60, "Unjustified temporal combination")
        if skew:
            require(bool(shot.get("synchronization_evidence")), "Missing synchronization evidence")
        require(bool(shot.get("coverage_evidence")), "Missing spatial coverage review")
        require(bool(shot.get("features")), "Empty snapshot")
        seen, geometries, rows = set(), [], []
        for feature in shot["features"]:
            p = feature["properties"]
            require(p["id"] not in seen, "Duplicate sector")
            seen.add(p["id"])
            require(p.get("area_evidence") and p.get("density_evidence"),
                "Missing measurement provenance")
            require(p.get("source_ids"), "Missing photographic sources")
            for asset_id in p["source_ids"]:
                a = registry[asset_id]
                require(a.get("admitted_for_counting") is True and a.get("pixel_review") is True
                    and a.get("authenticity_evidence"), "Unreviewed or unverified photograph")
                require(abs((timestamp(a["capture_time"])-t).total_seconds()) <= skew,
                    "Photograph from another time")
            g = metric_geometry(feature["geometry"])
            for other in geometries:
                require(g.intersection(other).area < 0.001, "Overlapping sectors double-count people")
            geometries.append(g)
            u = number(p["area_uncertainty_fraction"])
            require(0 <= u < 1, "Invalid area uncertainty")
            d = [number(v) for v in p["density_ppm2"]]
            require(len(d) == 3 and 0 <= d[0] <= d[1] <= d[2], "Invalid density bounds")
            require(p.get("uncertainty_evidence"), "Uncertainty requires evidence")
            counts = [g.area*(1-u)*d[0], g.area*d[1], g.area*(1+u)*d[2]]
            rows.append({"id":p["id"], "area_m2":g.area, "density_ppm2":d,
                "counts_low_central_high":counts})
        totals = [sum(r["counts_low_central_high"][i] for r in rows) for i in range(3)]
        output["snapshots"].append({"id":shot["id"], "time":shot["time"],
            "coverage_complete":shot.get("coverage_complete") is True,
            "sectors":rows, "counts_low_central_high":totals})
    complete = [s for s in output["snapshots"] if s["coverage_complete"]]
    if complete:
        output["observed_max"] = {
            "low":max(s["counts_low_central_high"][0] for s in complete),
            "central_scenario":max(s["counts_low_central_high"][1] for s in complete),
            "high":max(s["counts_low_central_high"][2] for s in complete)}
        output["status"] = "observed_snapshots_only"
        output["reason"] = "Maximum over reviewed snapshots does not prove the event-wide peak."
    else:
        output["reason"] = "Partial spatial coverage; no whole-crowd estimate."
    return output

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/measurements.json")
    ap.add_argument("--assets", default="data/assets.json")
    ap.add_argument("--output", default="results/estimate.json")
    args = ap.parse_args()
    result = calculate(json.loads(Path(args.data).read_text()),
        json.loads(Path(args.assets).read_text())["assets"])
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
