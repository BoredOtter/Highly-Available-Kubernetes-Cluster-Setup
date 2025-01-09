# Highly Available Kubernetes Cluster Setup

This repository contains Ansible playbooks for configuring hosts and setting up a highly available Kubernetes cluster based on RKE2 with Cilium CNI and ArgoCD.

## Prerequisites

1. **Install Ansible**: Ensure Ansible is installed on your local machine.
2. **Access Permissions**: Access the target hosts with appropriate permissions.
3. **Create Ansible Vault File**: Create an Ansible Vault file with the following contents:
    ```yaml
    argo:
      serverAdminPassword: "{{ argo.serverAdminPassword }}"
      webhook_github_secret: "{{ argo.webhook_github_secret }}"
    ```

## Setting up the Cluster

1. **Prepare the Hosts**:
    ```sh
    ansible-playbook -i inventory.yaml prepare_hosts.yaml
    ```

2. **Set up the Cluster**:
    ```sh
    ansible-playbook -i inventory.yaml setup_cluster.yaml --become --ask-become-pass --vault-password-file vaultcreds
    ```

3. **Set up ArgoCD in HA mode**:
    ```sh
    ansible-playbook -i inventory.yaml setup_argo.yaml --become --ask-become-pass --vault-password-file vaultcreds
    ```
