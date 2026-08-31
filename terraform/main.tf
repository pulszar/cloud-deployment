terraform {
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = "~> 3.0.2"
        }
    }
    required_version = "1.15.8"
}

provider "azurerm" {
    features {}
}

resource "azurerm_resource_group" "rg" {
    name = var.rg_name
    location = var.location
}

resource "azurerm_virtual_network" "vnet" {
    name = var.virtual_network_name
    location = var.location
    resource_group_name = var.rg_name

    address_space = ["10.0.0.0/16"]
}
