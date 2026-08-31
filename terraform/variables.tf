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

variable "network_interface_name" {
    default = "nic-deploy"
    description = "Resource will be placed in the Central US region"
    type = string
}
