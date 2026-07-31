#!/usr/bin/env python3
# © Siyuan (AI·LAB), CC BY 4.0
"""Merge stage claims into the fixed research claim register."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


STAGE_FILES = [
    "03-s1-foundations.json",
    "04-s2-business-model.json",
    "05-s2.5-landscape.json",
    "06-s3-user-pains.json",
    "07-s4-opportunities.json",
    "08-s5-product-architecture.json",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    parser.add_argument("--project", required=True)
    args = parser.parse_args()
    research_dir = Path(args.project_root).expanduser().resolve() / "research"
    claims = []
    seen: set[str] = set()
    for file_name in STAGE_FILES:
        path = research_dir / file_name
        data = json.loads(path.read_text(encoding="utf-8"))
        for claim in data["claims"]:
            claim_id = claim["id"]
            if claim_id in seen:
                raise SystemExit(f"ERROR: duplicate claim ID {claim_id}")
            seen.add(claim_id)
            claims.append(claim)
    output = {
        "schema_version": "1.0",
        "project": args.project,
        "claims": claims,
    }
    target = research_dir / "11-claim-register.json"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=research_dir, delete=False) as tmp:
        json.dump(output, tmp, ensure_ascii=False, indent=2)
        tmp.write("\n")
        tmp_path = Path(tmp.name)
    tmp_path.replace(target)
    print(f"merged {len(claims)} claims -> {target}")


if __name__ == "__main__":
    main()
