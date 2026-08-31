variable "rg_name" {
    default = "rg-deploy-test-01"
    description = "Hold resources related to this project"
    type = string
}

variable "location" {
    default = "Central US"
    description = "Resource will be placed in the Central US region"
    type = string
}

variable "virtual_network_name" {
    default = "vnet-deploy"
    description = "Virtual network"
    type = string
}

variable "subnet_app_name" {
    default = "subnet-app"
    description = "Subnet to hold our app VM"
    type = string
}

variable "network_interface_name" {
    default = "nic-app"
    description = "NIC that attaches to the app VM"
    type = string
}

variable "public_ip_name" {
    default = "public-ip-app"
    description = "Reach the app from outside Azure"
    type = string
}

variable "nic_ip_config_name" {
    default = "nic-ip-config"
    description = "Reach the app from outside Azure"
    type = string
}

variable "nsg_name" {
    default = "nsg-deploy"
    description = "Filter traffic into app subnet"
    type = string
}

variable "nsg_security_rule_name" {
    default = "nsg-sr-name"
    description = "Filter traffic into app subnet"
    type = string
}

variable "vm_name" {
    default = "vm-deploy-tst-01"
    description = "Filter traffic into app subnet"
    type = string
}

