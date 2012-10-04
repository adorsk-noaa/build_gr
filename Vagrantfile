# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
    config.vm.box = "lucid32"

    config.vm.network :hostonly, "192.168.33.10"

    # config.vm.share_folder "v-data", "/vagrant_data", "../data"

    config.vm.provision :chef_solo do |chef|
        chef.cookbooks_path = "../my-recipes/cookbooks"
        chef.roles_path = "../my-recipes/roles"
        chef.data_bags_path = "../my-recipes/data_bags"
        chef.add_recipe "mysql"
        chef.add_role "web"

        # You may also specify custom JSON attributes:
        chef.json = { :mysql_password => "foo" }
    end

end
