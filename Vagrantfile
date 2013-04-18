# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "precise32"
  config.vm.box_url = "http://files.vagrantup.com/precise32.box"

  config.vm.forward_port 80, 8080
  config.vm.forward_port 8000, 8000
  config.vm.forward_port 5555, 5555 

  config.vm.share_folder "v-app", "/usr/local/apps/growth-yield-batch", "./"

  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = "puppet/manifests"
    puppet.manifest_file  = "lot.pp"
    puppet.module_path = "puppet/modules"
    puppet.options = ["--templatedir","/vagrant/puppet/manifests/files", "--verbose", "--debug"]
  end
end
