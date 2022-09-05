# CLO5
[DEPRECATED]

This software is provided as is, the project has reached the end of its development and life. Feel free to browse the code, but no support or warranties will be provided. All credits goes to original developers and associates.

[Description]

POC for configuring instances with gitlab CI/CD and deploy on them python-flask based microservices.

## App documentation
[In apps folder->README.md](./apps/README.md)

## Requirements on deployer VM (not target VM)
Requirements on deployer VM (not target VM)
```bash
ansible-galaxy install -r requirements.yml
```

## Inventory setup

### Ansible inventory
Edit inventory/etna-clo5-lab.yml with target VM IP.
```
$ cat inventory/etna-clo5-lab.yml
test-vm ansible_host=10.0.0.1 ansible_ssh_user=user ansible_ssh_pass=pass ansible_become=yes   
```

## Usage 
You can either run all at once or play according which playbook you want.
```bash 
# [Optional] Check dynamic inventory configuration:
ansible-inventory -i inventory/etna-clo5-lab.yml --list
# Run playbook
ansible-playbook -i inventory/etna-clo5-lab.yml playbook.yaml
# Run step1
ansible-playbook infrastructure.yml -i inventory/etna-clo5-lab.yml
# or for atalamon:
ansible-playbook infrastructure.yml -i inventory/clo5-lab.yml
```

## FAQ:
### [Optional] Check if SSH Agent forwarding works
SSH Agent forwarding is needed to forward your key to do internal operations.
You can test that your local ssh key works by entering `ssh -T git@github.com` in the terminal of deployer VM:
```
$ ssh -T git@github.com
Hi <Your Username>! You've successfully authenticated [...]
```
If the above command provides you a different output, please do take a look at Github documentation regarding [SSH Agent forwarding](https://docs.github.com/en/developers/overview/using-ssh-agent-forwarding).

### Docker registry : server gave HTTP response to HTTPS client
When running such command on a remote machine:
```bash
docker pull 172.16.226.86:5000/alpine
```
You may encounter this kind of error:

`Error response from daemon: Get "https://172.16.226.86:5000/v2/": http: server gave HTTP response to HTTPS client`

This is due to the fact that the remote machine is not configured to accept HTTPS connections as it is not a requirement, and it works fine with HTTP by editing the remote machine's configuration file:

```bash
# Linux based
sudo vim /etc/docker/daemon.json
# MacOS
sudo vim ~/.docker/daemon.json
```

```
{
   "insecure-registries": [
    "172.16.226.86:5000"
  ]
}
```

Once done, restart the docker service and try again.

[Official documentation on the subject](https://docs.docker.com/registry/insecure/).

## License:

[MIT](LICENSE)