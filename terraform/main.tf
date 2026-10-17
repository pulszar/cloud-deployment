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
    depends_on = [ azurerm_resource_group.rg ]
}

# Create subnet to hold the VM
resource "azurerm_subnet" "app_subnet" {
    name = var.subnet_app_name
    resource_group_name = var.rg_name

    virtual_network_name = azurerm_virtual_network.vnet.name
    address_prefixes = ["10.0.0.0/24"]
}

resource "azurerm_public_ip" "public_ip" {
    name = var.public_ip_name
    location = var.location
    resource_group_name = var.rg_name

    sku = "Standard"
    allocation_method = "Static"

    depends_on = [ azurerm_resource_group.rg ]
}

resource "azurerm_network_interface" "nic" {
    name = var.network_interface_name
    location = var.location
    resource_group_name = var.rg_name

    ip_configuration {
        name = var.nic_ip_config_name
        public_ip_address_id = azurerm_public_ip.public_ip.id
        private_ip_address_allocation = "Dynamic"
        subnet_id = azurerm_subnet.app_subnet.id
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

    depends_on = [ azurerm_resource_group.rg ]
}

# Associate subnet and NSG
resource "azurerm_subnet_network_security_group_association" "subnet_nsg_asoc" {
    subnet_id = azurerm_subnet.app_subnet.id
    network_security_group_id = azurerm_network_security_group.nsg.id
}

# Finally create the VM
resource "azurerm_linux_virtual_machine" "vm" {
    name = var.vm_name
    location = var.location
    resource_group_name = var.rg_name
    admin_username = "azureadmin"

    # Configure SSH access
    admin_ssh_key {
        username = "azureadmin"
        # Must have a key pair named "cloud_vm"
        public_key = file("~/.ssh/cloud_vm.pub")
    }

    # Cheapest general purpose Ubuntu VM
    size = "Standard_D2als_v7"

    os_disk {
        caching = "ReadWrite"
        storage_account_type = "StandardSSD_LRS"
    }

    network_interface_ids = [ azurerm_network_interface.nic.id ]

    # Create an identity for the VM
    identity {
        type = "SystemAssigned"
    }

    # Choose image
    source_image_reference {
        publisher = "Canonical"
        offer = "ubuntu-25_04"
        sku = "server"
        version = "latest"
    }

    # Cloud-init
    user_data = base64encode(file("./cloud_config.yaml"))
}

# Assign "Key Vault Secrets User" to the VMs identity on the scope containing the specific Key Vault

data "azurerm_subscription" "current" {}

# TODO: Create variable for kv resource group

resource "azurerm_role_assignment" "example" {
    scope = "${data.azurerm_subscription.current.id}/resourceGroups/rg-kv-deploy/providers/Microsoft.KeyVault/vaults/kv-deploy-02"
    role_definition_name = "Key Vault Secrets User"
    principal_id = azurerm_linux_virtual_machine.vm.identity[0].principal_id
}