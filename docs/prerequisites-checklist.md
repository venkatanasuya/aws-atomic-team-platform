# Prerequisites checklist

## Local tools
- [ ] VS Code
- [ ] Git
- [ ] Terraform CLI
- [ ] Python 3.10+
- [ ] AWS CLI v2
- [ ] PowerShell 7
- [ ] Internet access for Terraform provider downloads

## AWS account readiness
- [ ] Root MFA enabled
- [ ] Billing dashboard checked
- [ ] Budget and email alerts configured
- [ ] Correct account and region confirmed
- [ ] Use a dedicated demo profile / role; do not use root credentials for Terraform
- [ ] Credentials are active only if needed and are not committed to Git
- [ ] No deployment until local validation and plan review are complete

## Concepts to be ready to explain
- IAM user vs role, least privilege, MFA, credential chain
- S3 bucket naming and global uniqueness
- S3 Block Public Access, encryption, versioning, ownership controls
- Terraform init, validate, plan, apply, destroy, state
- Terraform provider and variables/tags
- AWS region and account context
- CloudTrail as audit trail; AWS Config and SCPs as broader governance options
- Difference between a local demo check and AWS-enforced authorization
- Cost attribution tags vs actual cost enforcement
