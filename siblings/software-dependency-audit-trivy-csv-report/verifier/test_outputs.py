import csv
import json
import os

W = "/root/work"
OUT = os.path.join(W, "high_critical.csv")
HEAD = ["Target", "Package", "Version", "CVE_ID", "Severity", "CVSS_Score", "Fixed_Version", "Title", "Url"]


def v3(v):
    c = v.get("CVSS") or {}
    for s in ("nvd", "ghsa", "redhat"):
        d = c.get(s) or {}
        if d.get("V3Score") is not None:
            return float(d["V3Score"])
    return None


def expected():
    with open(os.path.join(W, "trivy_report.json")) as f:
        data = json.load(f)
    rows = []
    for res in data.get("Results", []):
        for v in res.get("Vulnerabilities") or []:
            if v.get("Severity") not in ("HIGH", "CRITICAL"):
                continue
            sc = v3(v)
            rows.append({"Target": res["Target"], "Package": v["PkgName"], "Version": v["InstalledVersion"],
                         "CVE_ID": v["VulnerabilityID"], "Severity": v["Severity"],
                         "CVSS_Score": "N/A" if sc is None else "%.1f" % sc,
                         "Fixed_Version": v.get("FixedVersion") or "N/A",
                         "Title": v.get("Title", ""), "Url": v.get("PrimaryURL", "")})
    rows.sort(key=lambda r: (r["CVSS_Score"] == "N/A",
                             -float(r["CVSS_Score"]) if r["CVSS_Score"] != "N/A" else 0.0,
                             r["CVE_ID"]))
    return rows


def norm(r):
    r = {k: (r.get(k) or "").strip() for k in HEAD}
    if r["CVSS_Score"] != "N/A":
        try:
            r["CVSS_Score"] = "%.1f" % float(r["CVSS_Score"])
        except ValueError:
            pass
    return r


def actual():
    with open(OUT, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        return rd.fieldnames, [norm(r) for r in rd]


def test_file_exists():
    assert os.path.isfile(OUT)


def test_header():
    head, _ = actual()
    assert head == HEAD


def test_selected_cves():
    _, rows = actual()
    got = [r["CVE_ID"] for r in rows]
    exp = [r["CVE_ID"] for r in expected()]
    assert len(got) == len(exp)
    assert set(got) == set(exp)


def test_row_values():
    _, rows = actual()
    got = {r["CVE_ID"]: r for r in rows}
    for e in expected():
        assert e["CVE_ID"] in got
        assert got[e["CVE_ID"]] == e, (got[e["CVE_ID"]], e)


def test_order():
    _, rows = actual()
    assert [r["CVE_ID"] for r in rows] == [r["CVE_ID"] for r in expected()]
