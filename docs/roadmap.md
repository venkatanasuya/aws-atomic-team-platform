# Roadmap

## Phase 1 (this repository)
- Local JSON request validation
- One approved resource type (private S3 bucket)
- Terraform plan and gated apply/destroy
- Mandatory team/project/cost metadata
- Unit tests and demo runbook

## Phase 2
- Add CI validation and pull-request review
- Add least-privilege IAM role and OIDC for CI
- Configure remote Terraform state and locking
- Add policy-as-code checks

## Phase 3
- Add additional modules (Secrets Manager, SQS, DynamoDB) with resource-specific security requirements
- Add audit/event reporting
- Add approval gates for production
- Add an API or web UI only if it materially improves developer workflow
