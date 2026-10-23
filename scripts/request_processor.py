#!/usr/bin/env python3
"""Small local demo processor: validate -> Terraform plan -> gated apply/destroy."""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TF_DIR = ROOT / "modules" / "s3_bucket"
ALLOWED_ENVIRONMENTS = {"dev", "test", "stage", "prod"}
ALLOWED_REGIONS = {"us-east-1"}
REQUIRED = {
    "request_id", "resource_type", "team_name", "team_owner",
    "application_name", "environment", "project", "cost_center",
    "region", "bucket_suffix", "purpose"
}
PATTERNS = {
    "team_name": r"^[a-z0-9-]{2,32}$",
    "application_name": r"^[a-z0-9-]{2,40}$",
    "project": r"^[a-z0-9-]{2,40}$",
    "cost_center": r"^[A-Za-z0-9-]{2,24}$",
    "bucket_suffix": r"^[a-z0-9-]{3,30}$",
}

def load_request(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Request must be a JSON object.")
    missing = sorted(REQUIRED - set(data))
    extra = sorted(set(data) - REQUIRED)
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))
    if extra:
        raise ValueError("Unsupported fields: " + ", ".join(extra))
    if data["resource_type"] != "s3_bucket":
        raise ValueError("Only resource_type='s3_bucket' is allowed in this demo.")
    if data["environment"] not in ALLOWED_ENVIRONMENTS:
        raise ValueError("environment must be one of: " + ", ".join(sorted(ALLOWED_ENVIRONMENTS)))
    if data["region"] not in ALLOWED_REGIONS:
        raise ValueError("region is restricted to us-east-1 for this demo.")
    for field, pattern in PATTERNS.items():
        if not isinstance(data[field], str) or not re.fullmatch(pattern, data[field]):
            raise ValueError(f"Invalid value for {field}: must match {pattern}")
    for field in ("request_id", "team_owner", "purpose"):
        if not isinstance(data[field], str) or not data[field].strip():
            raise ValueError(f"{field} must be a non-empty string.")
    if len(data["team_owner"]) > 120 or len(data["purpose"]) > 200 or len(data["request_id"]) > 80:
        raise ValueError("One or more text fields exceed the allowed length.")
    return data

def bucket_name(data):
    # Keep globally unique name within S3's 63-character limit.
    raw = f"atp-{data['team_name']}-{data['environment']}-{data['bucket_suffix']}"
    return raw[:63].strip("-")

def run(cmd, env=None):
    print("\n> " + " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=TF_DIR, env=env, check=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["validate", "plan", "apply", "destroy"])
    parser.add_argument("request", help="Path to request JSON")
    parser.add_argument("--profile", default=os.environ.get("AWS_PROFILE", ""),
                        help="AWS CLI profile (e.g. fde-dev); optional if using role/credential chain")
    args = parser.parse_args()

    request_path = Path(args.request)
    if not request_path.is_absolute():
        request_path = (Path.cwd() / request_path).resolve()
    try:
        data = load_request(request_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"REQUEST REJECTED: {exc}", file=sys.stderr)
        return 2

    name = bucket_name(data)
    tags = {
        "Team": data["team_name"],
        "TeamOwner": data["team_owner"],
        "Application": data["application_name"],
        "Environment": data["environment"],
        "Project": data["project"],
        "CostCenter": data["cost_center"],
        "RequestId": data["request_id"],
    }
    print("REQUEST VALIDATED")
    print(f"  Request:      {data['request_id']}")
    print(f"  Team:         {data['team_name']}")
    print(f"  Environment:  {data['environment']}")
    print(f"  Region:       {data['region']}")
    print(f"  Resource:     S3 bucket {name}")
    print("  Tags:         " + ", ".join(f"{k}={v}" for k, v in tags.items()))
    if args.action == "validate":
        print("VALIDATION ONLY: no AWS calls and no resources created.")
        return 0

    # Profile is passed to the provider via a temporary generated tfvars file.
    vars_payload = {
        "aws_region": data["region"],
        "aws_profile": args.profile,
        "bucket_name": name,
        "tags": tags,
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".auto.tfvars.json",
                                     encoding="utf-8", delete=False) as f:
        json.dump(vars_payload, f, indent=2)
        vars_path = Path(f.name)

    env = os.environ.copy()
    try:
        run(["terraform", "init", "-input=false"], env=env)
        run(["terraform", "validate"], env=env)
        if args.action == "plan":
            run(["terraform", "plan", "-input=false", "-var-file", str(vars_path),
                 "-out", "demo.tfplan"], env=env)
            print("\nPLAN COMPLETE. No resources were created.")
            print("Review the plan before choosing the explicit apply command.")
            return 0
        if args.action == "apply":
            # Resolve the account identity before prompting; this is a read-only STS call.
            cmd = ["aws", "sts", "get-caller-identity", "--output", "json"]
            if args.profile:
                cmd += ["--profile", args.profile]
            identity = json.loads(subprocess.check_output(cmd, text=True))
            print(f"\nTARGET AWS ACCOUNT: {identity.get('Account', 'unknown')}")
            print(f"TARGET AWS ARN:     {identity.get('Arn', 'unknown')}")
            print(f"TARGET REGION:      {data['region']}")
            print("This operation creates a real S3 bucket. Confirm that the account is correct.")
            if input("Type APPLY to continue: ").strip() != "APPLY":
                print("Cancelled.")
                return 1
            run(["terraform", "apply", "-input=false", "-auto-approve",
                 "-var-file", str(vars_path)], env=env)
            print("\nAPPLY COMPLETE.")
            return 0
        if args.action == "destroy":
            print("\nWARNING: destroy affects resources tracked in this module's local Terraform state.")
            print("Ensure this is only the demo bucket and remove any objects first.")
            if input("Type DESTROY to continue: ").strip() != "DESTROY":
                print("Cancelled.")
                return 1
            run(["terraform", "destroy", "-input=false", "-auto-approve",
                 "-var-file", str(vars_path)], env=env)
            print("\nDESTROY COMPLETE.")
            return 0
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode or 1
    finally:
        try:
            vars_path.unlink(missing_ok=True)
        except OSError:
            pass
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
