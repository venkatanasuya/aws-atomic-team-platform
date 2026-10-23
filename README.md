# AWS Atomic Team Self-Service Platform

A demo internal developer platform (IDP) for AWS. Application teams submit a JSON request; a local request processor validates it and invokes Terraform to plan or, only with an explicit flag, apply a private S3 bucket with encryption, versioning, public-access blocking, and mandatory ownership tags.

> **Safety first:** This repository does not contain AWS credentials and does not deploy anything during validation. Start with `validate` and `plan`. `apply` creates billable resources and must be explicitly requested.

## What this demonstrates

- Atomic-team ownership through `team_name`, `team_owner`, `application_name`, `environment`, and `cost_center`
- Self-service request validation and approved resource types
- Reusable Terraform module
- Secure S3 defaults: public access blocked, server-side encryption, versioning
- Mandatory tags for ownership, environment, project, and cost attribution
- Separation of request validation, Terraform planning, and deployment
- A path to CI/CD and stronger organization-wide governance

## Architecture

1. A team submits a request JSON file in `requests/`.
2. `scripts/request_processor.py` validates required fields and allow-listed values.
3. The processor writes a temporary Terraform variables file.
4. Terraform initializes, validates, and creates a plan.
5. Only `python scripts/request_processor.py apply requests/payments-dev.json` proceeds to apply, after an interactive confirmation.

This is a **portfolio/demo reference implementation**, not a production service or an authenticated web portal. The local script is not an authorization boundary: production deployments must enforce permissions in AWS IAM and organization-level controls, not trust user-supplied JSON.

## Prerequisites

- Windows 11, VS Code, PowerShell 7, and Git
- Terraform CLI (1.6+ recommended; use your installed version if current)
- Python 3.10+
- AWS account with root MFA and billing alerts/budget configured
- AWS CLI v2 configured for a named profile, preferably a dedicated least-privilege demo role/user with MFA
- Network access to download Terraform providers

Do not put access keys, session tokens, passwords, or account secrets in this repository. Do not commit `.aws/`, state files, plan files, or `*.tfvars`.

## Step 0 — Verify local tools (PowerShell)

```powershell
git --version
terraform version
python --version
aws --version
aws sts get-caller-identity --profile fde-dev
```

The last command only checks identity; it does not create resources. Replace `fde-dev` with your configured AWS CLI profile. If your access key remains deactivated, do not reactivate it just for this project. Prefer AWS IAM Identity Center/role-based credentials if available, or create a dedicated credential only after reviewing the security and MFA setup.

## Step 1 — Clone or open the repository

Extract the ZIP, then:

```powershell
cd .\aws-atomic-team-platform
```

## Step 2 — Validate request locally (no AWS resources)

```powershell
python .\scripts\request_processor.py validate .\requests\payments-dev.json
python -m unittest discover -s tests -v
```

These commands do not call AWS or create resources.

## Step 3 — Check AWS identity (read-only)

```powershell
aws sts get-caller-identity --profile fde-dev
```

Confirm the account is your intended personal demo account. Do not continue if the account is unexpected.

## Step 4 — Terraform plan (no resource creation)

```powershell
python .\scripts\request_processor.py plan .\requests\payments-dev.json --profile fde-dev
```

Terraform may download its provider and create local `.terraform/`, state metadata, and plan files. `plan` should not create the S3 bucket, but it can make read-only AWS API calls. Review the plan carefully.

## Step 5 — Optional deployment (creates a real S3 bucket)

Only do this after you have checked the account, region, expected cost, and plan:

```powershell
python .\scripts\request_processor.py apply .\requests\payments-dev.json --profile fde-dev
```

The script prints the target account and asks you to type `APPLY` before proceeding. This is a convenience safeguard, not a substitute for IAM permissions or code review.

## Step 6 — Verify and clean up

After a successful apply:

```powershell
terraform -chdir=.\modules\s3_bucket output
aws s3api get-public-access-block --bucket <bucket-name> --profile fde-dev
aws s3api get-bucket-versioning --bucket <bucket-name> --profile fde-dev
```

If you uploaded objects, remove them first. Then destroy only this demo's resources using the same request and profile:

```powershell
python .\scripts\request_processor.py destroy .\requests\payments-dev.json --profile fde-dev
```

The script asks for confirmation. Terraform state is local in this demo; keep it private and do not delete state before cleanup. Do not use `destroy` against resources you did not create with this repository.

## Demo story

1. Show a valid request for the Payments team.
2. Show validation passing.
3. Show an invalid request (e.g. missing `team_owner`) failing before Terraform runs.
4. Show the Terraform plan and point out encryption, versioning, public access blocking, and tags.
5. If approved, deploy and verify the controls.
6. Explain that each atomic team owns its application and request while the platform team owns approved modules, guardrails, and paved-road workflows.

## Current scope and production gaps

This demo provisions one S3 bucket only. It does not provide a web UI, user authentication, approval workflow, multi-account orchestration, remote state locking, automated budget enforcement, or production-grade policy-as-code. Do not expose the processor as a service or use it as a security boundary.

Production evolution:
- Run CI/CD with OIDC and short-lived role credentials; avoid long-lived keys.
- Store Terraform state in a dedicated encrypted S3 backend with locking configured for your Terraform version.
- Enforce least privilege, permission boundaries, SCPs, and AWS Config/CloudTrail as appropriate.
- Add policy-as-code checks, code review, approval for production, and central audit logging.
- Consider a catalog/API/UI only after the core paved road works.
