provider "aws" {
  region = "ap-south-1"
}

variable "environment" {
  default = "development"
}

resource "aws_instance" "demo" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  user_data = <<-EOF
    #!/bin/bash
    export DB_PASSWORD="MySecretPassword123"
  EOF
}