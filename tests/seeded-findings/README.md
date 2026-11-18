# Seeded findings

Each folder holds one finding planted on purpose, for one scanner (D-013). CI runs
`kiln scan <scanner> --seeded` on it, which succeeds only if the scanner reports the planted
finding at a blocking severity. An empty report from a broken scanner looks exactly like a
clean one; this is how CI tells them apart.

Nothing here is imported, installed, built or run. The repo scans exclude this folder
(`config/kiln.yaml`, `scanners`), and OSV-Scanner's fixture has a file name that no tool reads
on its own.

| Scanner | Fixture | Must report |
| --- | --- | --- |
| Semgrep | `semgrep/seeded.py` | `python.lang.security.audit.subprocess-shell-true` (high) |
| OSV-Scanner | `osv-scanner/seeded-requirements`, read as `requirements.txt` | `CVE-2020-14343` (critical) |
| Trivy | `trivy/Dockerfile` | `DS-0002` (high) |
