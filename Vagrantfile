# -*- mode: ruby -*-
# vi: set ft=ruby :
#
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"

  # config.vm.network "forwarded_port", guest: 80, host: 8080
  # config.vm.synced_folder "../data", "/vagrant_data"

  # config.vm.provider "virtualbox" do |vb|
  #   # Customize the amount of memory on the VM:
  # end

  config.vm.provision "shell", path: "ops/provision.sh"
end
