import json
import random

random.seed(20240611)
PKGS = ["lodash", "minimist", "express", "axios", "semver", "tar", "ip", "qs", "ws",
        "jsonwebtoken", "moment", "debug", "glob", "follow-redirects", "undici",
        "braces", "cookie", "path-to-regexp", "body-parser", "ejs"]
SEVS = ["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"]
ISSUES = ["Prototype pollution", "ReDoS in parser", "Path traversal, symlink handling",
          "Arbitrary code execution", "Header injection", "Denial of service via crafted input",
          "Improper input validation", "Information exposure"]


def ver():
    return "%d.%d.%d" % (random.randint(0, 9), random.randint(0, 20), random.randint(0, 15))


used = set()
results = []
for target in ["package-lock.json", "frontend/package-lock.json", "tools/package-lock.json"]:
    vulns = []
    for i in range(random.randint(10, 14)):
        pkg = random.choice(PKGS)
        while True:
            cve = "CVE-%d-%d" % (random.randint(2018, 2025), random.randint(1000, 49999))
            if cve not in used:
                used.add(cve)
                break
        v = {"VulnerabilityID": cve, "PkgName": pkg, "InstalledVersion": ver(),
             "Severity": random.choices(SEVS, weights=[2, 3, 4, 3, 1])[0],
             "Title": "%s: %s" % (pkg, random.choice(ISSUES)),
             "PrimaryURL": "https://avd.aquasec.com/nvd/" + cve.lower()}
        r = random.random()
        if r < 0.55:
            v["FixedVersion"] = ver()
        elif r < 0.7:
            v["FixedVersion"] = ver() + ", " + ver()
        elif r < 0.8:
            v["FixedVersion"] = ""
        cvss = {}
        for src in ["nvd", "ghsa", "redhat"]:
            r = random.random()
            if r < 0.4:
                d = {"V3Score": round(random.uniform(1.0, 10.0), 1)}
                if random.random() < 0.5:
                    d["V2Score"] = round(random.uniform(1.0, 10.0), 1)
                cvss[src] = d
            elif r < 0.6:
                cvss[src] = {"V2Score": round(random.uniform(1.0, 10.0), 1)}
            elif r < 0.65:
                cvss[src] = {"V3Score": None, "V2Score": round(random.uniform(1.0, 10.0), 1)}
        if cvss:
            v["CVSS"] = cvss
        vulns.append(v)
    results.append({"Target": target, "Class": "lang-pkgs", "Type": "npm", "Vulnerabilities": vulns})
results.insert(1, {"Target": "docs/package-lock.json", "Class": "lang-pkgs", "Type": "npm"})
report = {"SchemaVersion": 2, "ArtifactName": ".", "ArtifactType": "filesystem", "Results": results}
with open("trivy_report.json", "w") as f:
    json.dump(report, f, indent=1)
