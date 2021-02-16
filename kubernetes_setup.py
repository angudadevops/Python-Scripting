import subprocess
from subprocess import STDOUT, check_call
import apt
import sys
import os
import time

def install_pkg():
    try:
        check_call(["curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["sudo apt-key fingerprint 0EBFCD88"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(['sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"'], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["sudo mkdir -p  /etc/apt/sources.list.d/"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(['echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list'], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["sudo apt update"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        pkg_name = ["apt-transport-https", "ca-certificates", "curl", "gnupg-agent", "software-properties-common", "docker-ce=5:19.03.12~3-0~ubuntu-bionic", "docker-ce-cli=5:19.03.12~3-0~ubuntu-bionic", "containerd.io", "kubelet=1.18.8-00", "kubectl=1.18.8-00", "kubeadm=1.18.8-00"]
        for item in pkg_name:
            print("Installing {}".format(item))
            check_call(["sudo", "apt", "install", "--allow-downgrades", "-y", item], stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["sudo systemctl start docker"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["sudo systemctl enable docker"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["sudo apt-mark hold kubelet kubeadm kubectl"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["sudo swapoff -a"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
    except Exception as e:
        print(e)



def install_k8s():
    try:
        kube = check_call(["kubectl cluster-info"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        if kube == 0:
            print("**********************************************")
            print("Kubernetes Cluster is up and running")
            print("**********************************************")
            print(" ")
            check_call(["kubectl get pods -A"], shell=True)
        elif kube != 0:
            print("Kubernetes Cluster is starting")
    except Exception as e:
        print(" ")
        print("**********************************************")
        print("Installing Docker and Kubernetes Dependencies")
        print("**********************************************")
        print(" ")
        install_pkg()
        print(" ")
        print("**********************************************")
        print("Installing Kubernetes Cluster")
        print("**********************************************")
        print(" ")
        check_call(["sudo kubeadm reset --force"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        print("Initializing kubernetes cluster 'sudo kubeadm init --pod-network-cidr=192.168.0.0/16'")
        check_call(["sudo kubeadm init --pod-network-cidr=192.168.0.0/16"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["sudo rm -rf $HOME/.kube"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["mkdir -p $HOME/.kube"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["sudo chown $(id -u):$(id -g) $HOME/.kube/config"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        print("Applying Calico CNI to kubernetes cluster")
        check_call(["kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["kubectl taint nodes --all node-role.kubernetes.io/master-"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        time.sleep(15)
        print(" ")
        print("Kubeadm Token to Join the workers to the cluster")
        print(" ")
        print('-' * 150)
        #print("-------------------------------------------------------------------------------------------------")
        check_call(["sudo kubeadm token create --print-join-command"], shell=True, stderr=open(os.devnull,'wb'))
        print('-' * 150)
        print(" ")
        print("**********************************************")
        print("Kubernetes cluster is up and running")
        print("**********************************************")
        print(" ")
        check_call(["kubectl get pods -A"], shell=True)

def remove_reset():
    print("**********************************************")
    print("Remove and Reset cluster")
    print("**********************************************")
    try:
       check_call(["sudo kubeadm reset --force"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
       check_call(["sudo rm -rf $HOME/.kube"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
       check_call(["sudo apt autoremove -y"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
       check_call(["sudo apt purge -y --allow-change-held-packages kubelet kubeadm kubectl docker-ce* container* "], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
       check_call(["sudo rm -rf /var/lib/etcd /etc/kubernetes /usr/bin/helm /var/lib/docker /etc/docker /var/log/containers"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
    except Exception as e:
        print(e)
        check_call(["sudo apt purge -y --allow-change-held-packages kubelet kubeadm kubectl docker-ce* container* "], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)
        check_call(["sudo rm -rf /var/lib/etcd /etc/kubernetes /usr/bin/helm /var/lib/docker /etc/docker /var/log/containers"], shell=True, stdout=open(os.devnull,'wb'), stderr=STDOUT)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: \n \n   python kubernetes_setup.py install:    Install Kubernetes stack\n   python kubernetes_setup.py uninstall:  Uninstall Kubernetes stack")
        sys.exit()
    elif len(sys.argv) == 2:
        if sys.argv[1] == "install":
            install_k8s()
        elif sys.argv[1] == "uninstall":
            remove_reset()
    else:
        print("Usage: \n   python kubernetes_setup.py install:    Install Kubernetes stack\n   python kubernetes_setup.py uninstall:  Uninstall Kubernetes stack")
        sys.exit()
