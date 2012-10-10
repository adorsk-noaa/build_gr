# Define georefine dir.
georefine_dir = "/home/georefine"

# Define virtualenv dir.
georefine_venv = "#{georefine_dir}/venv"

# Global var for py version.
$py_version = ''

# Create user.
georefine_user = 'georefine'
georefine_user_pass = '$1$JXYcj8zJ$6hqs7XNGzj7aWCScX6FZi.'

user georefine_user do
    home    georefine_dir    
    supports     :manage_home => true
end

# Create folder for virtualenv, releases, data, and public files.
['releases', 'data', 'public', 'wsgi'].each do |dir_|
    dir_path = "#{georefine_dir}/#{dir_}"
    directory dir_path do
        owner georefine_user
        group georefine_user
    end
end

# DB connection.
georefine_db_connection = {
    :host => "localhost",
    :port => 5432,
    :username => 'postgres',
    :password => node['postgresql']['password']['postgres']
}

# Setup DB user.
georefine_db = 'georefine'
georefine_db_user = 'georefine'
georefine_db_password = 'georefine' #@TODO: read from node attributes or dbag.
postgresql_database_user georefine_db_user do
    connection georefine_db_connection
    password georefine_db_password
    action :create
end

# Spatialize db (will be trigger after db is created.)
postgis_contrib_dir = "/usr/share/postgresql/#{node['postgresql']['version']}/contrib/postgis-1.5"
postgis_sql = "#{postgis_contrib_dir}/postgis.sql"
postgis_srs_sql = "#{postgis_contrib_dir}/spatial_ref_sys.sql"

spatialize_command = <<-eos
    createlang plpgsql georefine; psql -d georefine -f #{postgis_sql};
    psql -d georefine -f #{postgis_srs_sql};
eos
['geometry_columns', 'geography_columns', 'spatial_ref_sys'].each do |table|
    spatialize_command += "echo 'GRANT ALL ON #{table} TO #{georefine_db_user};' | psql -d georefine;"
end

execute 'spatialize db' do
    command spatialize_command
    user 'postgres'
    action :nothing
end

# Create db.
postgresql_database "#{georefine_db}" do
    connection georefine_db_connection
    owner georefine_db_user
    action :create
    notifies :run, resources(:execute => 'spatialize db')
end

# Setup apache config.
web_app "georefine" do
    template "georefine.conf.erb"
    server_name "georefine.local"
    server_aliases [node['fqdn']]
    docroot "#{georefine_dir}/public"
    app_path "/georefine"
    app_wsgi_script_dir "#{georefine_dir}/wsgi"
end

# Get mod wsgi python intepreter version.
py_version_block = ruby_block "get_mod_wsgi_interpreter_version" do
    block do
        current_mod_wsgi = `readlink -f /usr/lib/apache2/modules/mod_wsgi.so`
        $py_version = current_mod_wsgi.scan(/\.so-(.+)/)[0]
    end
    action :nothing
end
# We execute the block during compile time so we can use the py_version later.
py_version_block.run_action(:create)

# Create virtualenv for georefine.
python_virtualenv 'georefine_venv' do
    path georefine_venv
    owner georefine_user
    group georefine_user
    options '--no-site-packages'
    interpreter "python#{$py_version}"
    action :create
end

# Install python libs. Will be triggered by creation of virtualenv.
[
    'sqlalchemy', 
    'geoalchemy', 
    'Flask', 
    'Flask-Admin',
    'Flask-OpenID',
    'Flask-Login',
    'psycopg2',
].each do |lib|
    python_pip lib do
        virtualenv georefine_venv
        action :nothing
        subscribes :install, resources(:python_virtualenv => 'georefine_venv')
    end
end

# Install mapscript. Will be trigger by creation of virtualenv.
#@TODO: hack! copies from sys dir. Should make this independent later by building
# standalone mapscript.
package "python-mapscript" do
    action :nothing
    subscribes :install, resources(:python_virtualenv => 'georefine_venv')
end

# Install libgdal-dev, necessary for fiona python lib. Will be trigger by creation of virtualenv.
package "libgdal-dev" do
    action :nothing
    subscribes :install, resources(:python_virtualenv => 'georefine_venv')
end

# Install fiona and shapely, will be triggered by installation of libgdal-dev.
['fiona', 'shapely'].each do |lib|
    python_pip lib do
        virtualenv georefine_venv
        action :nothing
        subscribes :install, resources(:package => 'libgdal-dev')
    end
end

execute "copy_mapscript" do
    command "cp /usr/lib/python#{$py_version}/dist-packages/*mapscript* #{georefine_venv}/lib/python#{$py_version}/site-packages/"
    action :nothing
    subscribes :run, resources(:python_virtualenv => 'georefine_venv')
end

# Install json gem during compile phase, for use later.
json_gem = gem_package 'json'
json_gem.run_action(:install)
require 'json'

# Write out node data to a file the deploy system can download.
file "node.json" do
    path "#{georefine_dir}/node.json"
    mode 0770
    owner georefine_user
    group georefine_user
    content JSON.dump({
        'db' => {
            'name' => georefine_db,
            'user' => georefine_db_user,
            'pass' => georefine_db_password,
            'port' => 5432,
            'host' => 'localhost'
        }
    })
end




# Setup app config.
