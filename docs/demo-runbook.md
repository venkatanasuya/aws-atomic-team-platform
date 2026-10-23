# Demo runbook

## Narrative

"Atomic teams should be autonomous in delivering application outcomes. They should not each reinvent infrastructure, IAM, security, and governance. This platform offers a paved road: teams submit a standard request, and a shared platform validates it, applies approved infrastructure modules, and enforces secure defaults."

## 5-minute demo

1. Show `requests/payments-dev.json`.
2. Run the local validation command.
3. Run the invalid sample and show the request is rejected before Terraform.
4. Explain the Terraform module's public-access block, encryption, versioning, ownership controls, and tags.
5. Run a plan only after checking the active AWS identity and budget alerts.
6. Optionally deploy only if you intend to create a real bucket and can clean it up afterward.
7. Explain how the pattern could expand to Secrets Manager, queues, databases, and account-level vending after stronger controls are implemented.

## Questions to prepare for

- How is autonomy balanced with governance?
- Why is the request processor not itself a security boundary?
- Where are identity and authorization enforced?
- How are costs attributed to a team?
- How would you prevent public S3 access?
- How would production approval and audit work?
- How would you safely manage Terraform state?
- What is the difference between a request validation check and an AWS-enforced policy?
