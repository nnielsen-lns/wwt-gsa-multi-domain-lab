#!/usr/bin/env python3
import argparse, os, sys
from typing import Any, Dict, List, Optional
import requests, yaml

def die(msg: str, code: int = 1) -> None:
print(f"ERROR: {msg}", file=sys.stderr)
sys.exit(code)

def load_yaml(path: str) -> Dict[str, Any]:
with open(path, "r", encoding="utf-8") as f:
return yaml.safe_load(f) or {}

class NetBox:
def init(self, base_url: str, token: str, verify_tls: bool = False) -> None:
self.base_url = base_url.rstrip("/")
self.s = requests.Session()
self.s.headers.update({"Authorization": f"Token {token}", "Content-Type": "application/json", "Accept": "application/json"})
self.verify_tls = verify_tls
def _url(self, path: str) -> str:
    return f"{self.base_url}{path}"

def get_one(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    r = self.s.get(self._url(endpoint), params=params, verify=self.verify_tls)
    if r.status_code != 200:
        die(f"GET {endpoint} failed: {r.status_code} {r.text}")
    results = r.json().get("results", [])
    return results[0] if results else None

def create(self, endpoint: str, payload: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
    if dry_run:
        print(f"DRY-RUN POST {endpoint}: {payload}")
        return {"id": None, **payload}
    r = self.s.post(self._url(endpoint), json=payload, verify=self.verify_tls)
    if r.status_code not in (200, 201):
        die(f"POST {endpoint} failed: {r.status_code} {r.text}\nPayload: {payload}")
    return r.json()

def tag_ids(self, slugs: List[str]) -> List[int]:
    ids: List[int] = []
    for slug in slugs:
        obj = self.get_one("/api/extras/tags/", {"slug": slug})
        if not obj:
            die(f"Tag not found: {slug}")
        ids.append(obj["id"])
    return ids

def site_id(self, slug: str) -> int:
    obj = self.get_one("/api/dcim/sites/", {"slug": slug})
    if not obj:
        die(f"Site not found: {slug}")
    return obj["id"]

def vrf_id(self, name: str) -> int:
    obj = self.get_one("/api/ipam/vrfs/", {"name": name})
    if not obj:
        die(f"VRF not found: {name}")
    return obj["id"]

def role_id(self, slug: str) -> int:
    obj = self.get_one("/api/ipam/roles/", {"slug": slug})
    if not obj:
        die(f"Prefix role not found: {slug}")
    return obj["id"]

def main() -> None:
ap = argparse.ArgumentParser()
ap.add_argument("--apply", action="store_true")
ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--verify-tls", action="store_true")
args = ap.parse_args()


dry_run = not args.apply or args.dry_run

base_url = os.getenv("NETBOX_URL")
token = os.getenv("NETBOX_TOKEN")
if not base_url or not token:
    die("Set NETBOX_URL and NETBOX_TOKEN env vars.")

nb = NetBox(base_url, token, verify_tls=args.verify_tls)

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ydir = os.path.join(root, "netbox")

tags = load_yaml(os.path.join(ydir, "tags.yaml")).get("tags", [])
sites = load_yaml(os.path.join(ydir, "sites.yaml")).get("sites", [])
vrfs = load_yaml(os.path.join(ydir, "vrfs.yaml")).get("vrfs", [])
roles = load_yaml(os.path.join(ydir, "prefix_roles.yaml")).get("prefix_roles", [])
asns = load_yaml(os.path.join(ydir, "asns.yaml")).get("asns", [])

print(f"NetBox bootstrap (dry_run={dry_run}) -> {base_url}")

for t in tags:
    if nb.get_one("/api/extras/tags/", {"slug": t["slug"]}):
        print(f"SKIP tag {t['slug']}")
    else:
        nb.create("/api/extras/tags/", {"name": t["name"], "slug": t["slug"]}, dry_run)
        print(f"CREATE tag {t['slug']}")

for s in sites:
    if nb.get_one("/api/dcim/sites/", {"slug": s["slug"]}):
        print(f"SKIP site {s['slug']}")
    else:
        payload: Dict[str, Any] = {"name": s["name"], "slug": s["slug"]}
        if s.get("tags"):
            payload["tags"] = nb.tag_ids(s["tags"])
        nb.create("/api/dcim/sites/", payload, dry_run)
        print(f"CREATE site {s['slug']}")

for v in vrfs:
    if nb.get_one("/api/ipam/vrfs/", {"name": v["name"]}):
        print(f"SKIP vrf {v['name']}")
    else:
        payload = {"name": v["name"], "rd": v.get("rd"), "description": v.get("description", "")}
        nb.create("/api/ipam/vrfs/", payload, dry_run)
        print(f"CREATE vrf {v['name']}")

for r in roles:
    if nb.get_one("/api/ipam/roles/", {"slug": r["slug"]}):
        print(f"SKIP role {r['slug']}")
    else:
        nb.create("/api/ipam/roles/", {"name": r["name"], "slug": r["slug"]}, dry_run)
        print(f"CREATE role {r['slug']}")

for a in asns:
    if nb.get_one("/api/ipam/asns/", {"asn": a["asn"]}):
        print(f"SKIP asn {a['asn']}")
    else:
        nb.create("/api/ipam/asns/", {"asn": int(a["asn"]), "description": a.get("description", "")}, dry_run)
        print(f"CREATE asn {a['asn']}")

print("Bootstrap complete. (Prefixes will be added in the next commit.)")

if name == "main":
main()
