# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
    config.vm.box = "lucid32"

    config.vm.network :hostonly, "192.168.33.10"

    # config.vm.share_folder "v-data", "/vagrant_data", "../data"

    config.vm.provision :chef_solo do |chef|
        chef.cookbooks_path = ["chef/cookbooks", "chef/georefine_cookbooks"]
        chef.roles_path = "chef/roles"
        chef.data_bags_path = "chef/data_bags"
        chef.add_role "georefine_server"
    end

end
