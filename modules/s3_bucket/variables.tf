variable "aws_region" {
  description = "AWS region for the demo bucket"
  type        = string
  default     = "us-east-1"
  validation {
    condition     = var.aws_region == "us-east-1"
    error_message = "This demo is intentionally restricted to us-east-1."
  }
}

variable "aws_profile" {
  description = "AWS CLI profile name. Empty uses the standard AWS credential chain."
  type        = string
  default     = ""
}

variable "bucket_name" {
  description = "Globally unique S3 bucket name"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.bucket_name))
    error_message = "Bucket name must be 3-63 characters, lowercase, and use valid S3 bucket-name characters."
  }
}

variable "tags" {
  description = "Mandatory business ownership tags"
  type        = map(string)
  validation {
    condition = alltrue([
      for key in ["Team", "TeamOwner", "Application", "Environment", "Project", "CostCenter", "RequestId"] :
      contains(keys(var.tags), key) && trimspace(lookup(var.tags, key, "")) != ""
    ])
    error_message = "Tags must include Team, TeamOwner, Application, Environment, Project, CostCenter, and RequestId with non-empty values."
  }
}
