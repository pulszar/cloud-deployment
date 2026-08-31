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

# Create subnet to hold the VM
resource "azurerm_subnet" "app_subnet" {
    name = var.subnet_app_name
    resource_group_name = var.rg_name

    virtual_network_name = var.virtual_network_name
    address_prefixes = ["10.0.0.0/24"]
}

resource "azurerm_public_ip" "public_ip" {
    name = var.public_ip_name
    location = var.location
    resource_group_name = var.rg_name

    sku = "Standard"
    allocation_method = "Static"
}

resource "azurerm_network_interface" "nic" {
    name = var.network_interface_name
    location = var.location
    resource_group_name = var.rg_name

    ip_configuration {
        name = var.nic_ip_config_name
        public_ip_address_id = azurerm_public_ip.public_ip.id
        private_ip_address_allocation = "Static"
    }
}

resource "azurerm_network_security_group" "nsg" {
    name = var.nsg_name
    location = var.location
    resource_group_name = var.rg_name

    security_rule {
        name = var.nsg_security_rule_name
        direction = "Inbound"
        priority = 100
        protocol = "Tcp"
        access = "Allow"
        
        source_address_prefix = "*"
        source_port_range = "*"

        destination_address_prefix = "*"
        # Only allow ssh and http.
        # TODO: Change to just http once web server is setup
        destination_port_ranges = ["22", "80"]
    }
}

# Associate subnet and NSG
resource "azurerm_subnet_network_security_group_association" "subnet_nsg_asoc" {
    subnet_id = azurerm_subnet.app_subnet.id
    network_security_group_id = azurerm_network_security_group.nsg.id
}
