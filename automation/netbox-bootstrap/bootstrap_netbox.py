#!/usr/bin/env python3
"""
NetBox bootstrap for WWT GS&A multi-domain lab.

Reads YAML from ./netbox/*.yaml and creates/updates objects via NetBox API.

Supports:
- NetBox v1 tokens: Authorization: Token <token>
- NetBox v2 tokens: Authorization: Bearer <token>
(Override with NETBOX_AUTH_SCHEME=Token|Bearer)

Files expected (some optional):
- netbox/tags.yaml              { tags: [{name, slug}, ...] }
- netbox/sites.yaml             { sites: [{name, slug, tags:[...]} ...] }
- netbox/vrfs.yaml              { vrfs: [{name, rd, description} ...] }
- netbox/prefix_roles.yaml      { prefix_roles: [{name, slug} ...] }
- netbox/prefixes.yaml          { prefixes: [{prefix,status,site,role,tags,vrf?,description?} ...] }
- netbox/rirs.yaml              { rirs: [{name, slug, is_private:true}] }
- netbox/asns.yaml              { asns: [{asn,description,rir:slug}] }
- netbox/vrf_policy.yaml        { vrf_policy: [{name,vpn_id,rt,l3vni}] }   (custom fields)
"""

import argparse
import os
import sys
import json
import time
from typing import Any, Dict, Optional, List

import requests
import yaml


def die(msg: str) -> None:
    print(f"FATAL: {msg}", file=sys.stderr)
    sys.exit(1)


def load_yaml(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class NetBox:
    def __init__(
        self,
        base_url: str,
        token: str,
        auth_scheme: str = "Token",
        verify_tls: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.s = requests.Session()
        self.s.verify = verify_tls
        self.s.headers.update(
            {
                "Authorization": f"{auth_scheme} {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _url(self, path: str) -> str:
        if path.startswith("http"):
            return path
        return f"{self.base_url}{path}"

    def _req(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = self._url(path)
        r = self.s.request(method, url, params=params, json=payload, timeout=60)
        if r.status_code >= 400:
            detail = r.text
            raise RuntimeError(
                f"{method} {path} failed: {r.status_code} {detail}\nPayload: {payload}"
            )
        if r.status_code == 204:
            return None
        return r.json()

    def get_one(self, path: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = self._req("GET", path, params=params)
        results = data.get("results", [])
        return results[0] if results else None

    def get_all(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        params = params or {}
        out: List[Dict[str, Any]] = []
        url = path
        while True:
            data = self._req("GET", url, params=params)
            out.extend(data.get("results", []))
            nxt = data.get("next")
            if not nxt:
                break
            # next is full URL
            url = nxt
            params = None
        return out

    def create(
        self, path: str, payload: Dict[str, Any], dry_run: bool
    ) -> Optional[Dict[str, Any]]:
        if dry_run:
            return None
        return self._req("POST", path, payload=payload)

    def patch(self, path: str, payload: Dict[str, Any], dry_run: bool) -> None:
        if dry_run:
            return
        self._req("PATCH", path, payload=payload)

    # --- ID helpers ---
    def tag_id(self, slug: str) -> int:
        obj = self.get_one("/api/extras/tags/", {"slug": slug})
        if not obj:
            die(f"Tag not found: {slug}")
        return obj["id"]

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

    def rir_id(self, slug: str) -> int:
        obj = self.get_one("/api/ipam/rirs/", {"slug": slug})
        if not obj:
            die(f"RIR not found: {slug}")
        return obj["id"]

    # --- Content type for custom fields ---
    def content_type_id(self, app_label: str, model: str) -> int:
        # Not used. NetBox 4.5.x custom-fields can bind to content types by string like "ipam.vrf".
        raise RuntimeError("content_type_id() is not used in this bootstrap")

    def get_required_custom_fields_for(
        self, content_type: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Return {field_name: field_obj} for required custom fields bound to a given content type string, e.g. "ipam.vrf".
        """
        out: Dict[str, Dict[str, Any]] = {}
        fields = self.get_all("/api/extras/custom-fields/", {"limit": 200})
        for f in fields:
            if not f.get("required"):
                continue
            cts = f.get("content_types", []) or []
            if content_type in cts:
                out[f["name"]] = f
        return out

    def ensure_required_custom_fields_present(
        self,
        obj: Dict[str, Any],
        required_fields: Dict[str, Dict[str, Any]],
        defaults: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        If the object is missing any required custom field values, return a patched custom_fields dict; else None.
        """
        current = obj.get("custom_fields", {}) or {}
        changed = False
        new_cf = dict(current)

        for name in required_fields.keys():
            val = new_cf.get(name)
            if val is None or val == "":
                # apply a default if provided, else leave as-is (will still fail)
                if name in defaults:
                    new_cf[name] = defaults[name]
                    changed = True

        return new_cf if changed else None

    # --- Custom fields ---
    def ensure_custom_field(
        self,
        name: str,
        label: str,
        field_type: str,
        content_type_strs: List[str],
        required: bool,
        description: str = "",
        default: Any = None,
        dry_run: bool = True,
    ) -> None:
        existing = self.get_one("/api/extras/custom-fields/", {"name": name})
        if existing:
            cts = existing.get("object_types", []) or []
            if any(ct not in cts for ct in content_type_strs):
                new_cts = sorted(set(cts + content_type_strs))
                print(
                    f"PATCH custom_field {name} (add object_types {content_type_strs})"
                )
                self.patch(
                    f"/api/extras/custom-fields/{existing['id']}/",
                    {"object_types": new_cts},
                    dry_run,
                )
            else:
                print(f"SKIP custom_field {name}")
        else:
            payload = {
                "name": name,
                "label": label,
                "type": field_type,  # NetBox API type values: "text", "integer", etc.
                "required": required,
                "object_types": content_type_strs,
                "description": description,
            }
            if default is not None:
                payload["default"] = default

            print(f"CREATE custom_field {name}")
            self.create("/api/extras/custom-fields/", payload, dry_run)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run", action="store_true", help="Print actions without making changes"
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    parser.add_argument(
        "--verify-tls",
        action="store_true",
        help="Verify TLS certs (will fail with self-signed unless trusted)",
    )
    args = parser.parse_args()

    if args.dry_run and args.apply:
        die("Choose one: --dry-run or --apply")
    dry_run = True
    if args.apply:
        dry_run = False

    base_url = os.getenv("NETBOX_URL")
    token = os.getenv("NETBOX_TOKEN")
    if not base_url or not token:
        die("Set NETBOX_URL and NETBOX_TOKEN environment variables.")

    auth_scheme = os.getenv("NETBOX_AUTH_SCHEME")
    if not auth_scheme:
        auth_scheme = "Bearer" if str(token).startswith("nbxt_") else "Token"

    nb = NetBox(base_url, token, auth_scheme=auth_scheme, verify_tls=args.verify_tls)

    ydir = os.path.join(os.getcwd(), "netbox")

    tags = load_yaml(os.path.join(ydir, "tags.yaml")).get("tags", [])
    sites = load_yaml(os.path.join(ydir, "sites.yaml")).get("sites", [])
    vrfs = load_yaml(os.path.join(ydir, "vrfs.yaml")).get("vrfs", [])
    prefix_roles = load_yaml(os.path.join(ydir, "prefix_roles.yaml")).get(
        "prefix_roles", []
    )
    prefixes = load_yaml(os.path.join(ydir, "prefixes.yaml")).get("prefixes", [])
    rirs = load_yaml(os.path.join(ydir, "rirs.yaml")).get("rirs", [])
    asns = load_yaml(os.path.join(ydir, "asns.yaml")).get("asns", [])
    vrf_policy = load_yaml(os.path.join(ydir, "vrf_policy.yaml")).get("vrf_policy", [])

    print(
        f"NetBox bootstrap (dry_run={dry_run}) -> {base_url} (auth={auth_scheme}, verify_tls={args.verify_tls})"
    )

    # --- TAGS ---
    for t in tags:
        slug = t.get("slug") or t["name"].lower().replace(" ", "-")
        if nb.get_one("/api/extras/tags/", {"slug": slug}):
            print(f"SKIP tag {slug}")
        else:
            nb.create("/api/extras/tags/", {"name": t["name"], "slug": slug}, dry_run)
            print(f"CREATE tag {slug}")

    # --- SITES ---
    for s in sites:
        slug = s.get("slug") or s["name"].lower().replace(" ", "-")
        existing = nb.get_one("/api/dcim/sites/", {"slug": slug})
        tag_ids = (
            [nb.tag_id(tslug) for tslug in s.get("tags", [])] if s.get("tags") else []
        )
        if existing:
            # patch tags/name if needed
            patch: Dict[str, Any] = {}
            if existing.get("name") != s["name"]:
                patch["name"] = s["name"]
            if tag_ids:
                patch["tags"] = tag_ids
            if patch:
                print(f"PATCH site {slug}")
                nb.patch(f"/api/dcim/sites/{existing['id']}/", patch, dry_run)
            else:
                print(f"SKIP site {slug}")
        else:
            payload = {"name": s["name"], "slug": slug}
            if tag_ids:
                payload["tags"] = tag_ids
            nb.create("/api/dcim/sites/", payload, dry_run)
            print(f"CREATE site {slug}")

    # --- VRFs ---
    for v in vrfs:
        name = v["name"]
        existing = nb.get_one("/api/ipam/vrfs/", {"name": name})
        payload = {
            "name": name,
            "rd": v.get("rd", ""),
            "description": v.get("description", ""),
        }
        if existing:
            patch = {}
            # Only patch fields we manage
            for k in ("rd", "description"):
                if payload.get(k, "") != existing.get(k, ""):
                    patch[k] = payload[k]
            if patch:
                print(f"PATCH vrf {name}")
                nb.patch(f"/api/ipam/vrfs/{existing['id']}/", patch, dry_run)
            else:
                print(f"SKIP vrf {name}")
        else:
            nb.create("/api/ipam/vrfs/", payload, dry_run)
            print(f"CREATE vrf {name}")

    # --- PREFIX ROLES ---
    for r in prefix_roles:
        slug = r.get("slug") or r["name"].lower().replace(" ", "-")
        if nb.get_one("/api/ipam/roles/", {"slug": slug}):
            print(f"SKIP prefix_role {slug}")
        else:
            nb.create("/api/ipam/roles/", {"name": r["name"], "slug": slug}, dry_run)
            print(f"CREATE prefix_role {slug}")

    # --- RIRs (required for ASNs) ---
    for r in rirs:
        slug = r["slug"]
        if nb.get_one("/api/ipam/rirs/", {"slug": slug}):
            print(f"SKIP rir {slug}")
        else:
            payload = {
                "name": r["name"],
                "slug": slug,
                "is_private": bool(r.get("is_private", True)),
            }
            nb.create("/api/ipam/rirs/", payload, dry_run)
            print(f"CREATE rir {slug}")

    # --- ASNs ---
    for a in asns:
        asn = int(a["asn"])
        existing = nb.get_one("/api/ipam/asns/", {"asn": asn})
        rir_slug = a.get("rir") or "private-internal"
        rir_id = nb.rir_id(rir_slug)
        if existing:
            # patch description/rir if needed
            patch = {}
            if a.get("description", "") != existing.get("description", ""):
                patch["description"] = a.get("description", "")
            if existing.get("rir") != rir_id:
                patch["rir"] = rir_id
            if patch:
                print(f"PATCH asn {asn}")
                nb.patch(f"/api/ipam/asns/{existing['id']}/", patch, dry_run)
            else:
                print(f"SKIP asn {asn}")
        else:
            payload = {
                "asn": asn,
                "description": a.get("description", ""),
                "rir": rir_id,
            }
            nb.create("/api/ipam/asns/", payload, dry_run)
            print(f"CREATE asn {asn}")

    # --- PREFIXES ---
    for p in prefixes:
        prefix = p["prefix"]
        existing = nb.get_one("/api/ipam/prefixes/", {"prefix": prefix})
        payload: Dict[str, Any] = {
            "prefix": prefix,
            "status": p.get("status", "active"),
        }

        # Site + role are usually by slug/name in YAML; resolve to IDs
        if p.get("site"):
            payload["site"] = nb.site_id(p["site"])
        if p.get("role"):
            payload["role"] = nb.role_id(p["role"])

        # VRF is optional
        if p.get("vrf"):
            payload["vrf"] = nb.vrf_id(p["vrf"])

        # tags
        if p.get("tags"):
            payload["tags"] = [nb.tag_id(t) for t in p["tags"]]

        # optional description
        if p.get("description"):
            payload["description"] = p["description"]

        if existing:
            # Patch only what we manage
            patch: Dict[str, Any] = {}
            for k in ("status", "site", "role", "vrf", "description"):
                if k in payload:
                    if payload[k] != existing.get(k):
                        patch[k] = payload[k]
            if "tags" in payload:
                if payload["tags"] != existing.get("tags", []):
                    patch["tags"] = payload["tags"]
            if patch:
                print(f"PATCH prefix {prefix}")
                nb.patch(f"/api/ipam/prefixes/{existing['id']}/", patch, dry_run)
            else:
                print(f"SKIP prefix {prefix}")
        else:
            nb.create("/api/ipam/prefixes/", payload, dry_run)
            print(f"CREATE prefix {prefix}")

    # --- VRF CUSTOM FIELDS + POLICY POPULATION ---
    if vrf_policy:
        ct_strs = ["ipam.vrf"]

        nb.ensure_custom_field(
            name="vpn_id",
            label="VPN ID",
            field_type="integer",
            content_type_strs=ct_strs,
            required=False,
            description="SD-WAN VPN identifier (e.g., 900/920/930/940).",
            dry_run=dry_run,
        )
        nb.ensure_custom_field(
            name="rt",
            label="Route Target",
            field_type="text",
            content_type_strs=ct_strs,
            required=False,
            description="Canonical RT for this VRF (e.g., 65000:920).",
            dry_run=dry_run,
        )
        nb.ensure_custom_field(
            name="l3vni",
            label="L3VNI",
            field_type="integer",
            content_type_strs=ct_strs,
            required=False,
            description="EVPN L3VNI for this VRF (e.g., 10920).",
            dry_run=dry_run,
        )

        # Apply policy to VRFs
        for vp in vrf_policy:
            name = vp["name"]
            vrf_obj = nb.get_one("/api/ipam/vrfs/", {"name": name})
            if not vrf_obj:
                die(f"vrf_policy references VRF that does not exist: {name}")

            desired_cf = {
                "vpn_id": vp.get("vpn_id", None),
                "rt": vp.get("rt", None),
                "l3vni": vp.get("l3vni", None),
            }

            current_cf = vrf_obj.get("custom_fields", {}) or {}
            patch_needed = False
            for k, v in desired_cf.items():
                if current_cf.get(k) != v:
                    patch_needed = True
                    break

            if patch_needed:
                print(f"PATCH vrf custom_fields {name} -> {desired_cf}")
                nb.patch(
                    f"/api/ipam/vrfs/{vrf_obj['id']}/",
                    {"custom_fields": desired_cf},
                    dry_run,
                )
            else:
                print(f"SKIP vrf custom_fields {name}")

    print("Done.")


if __name__ == "__main__":
    main()
