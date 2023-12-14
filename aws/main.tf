terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 3.0"
        }
    }
}

# Configure the AWS Provider
provider aws {
    profile = "default"
    region = "eu-west-2"
    shared_credentials_files = [ "~/.aws/credentials" ]
}

# Create a VPC
resource "aws_vpc" "app_vpc" {
    cidr_block = ""
}