# Define georefine dir.
georefine_dir = "/home/georefine"

# Create user.
georefine_user = 'georefine'
user georefine_user do
    home    georefine_dir    
    supports     :manage_home => true
end

# Create folder for code, data, and public files.
['lib', 'data', 'public'].each do |dir_|
    dir_path = "#{georefine_dir}/#{dir_}"
    directory dir_path do
        owner georefine_user
    end
end

# Setup DB.
georefine_db_user = 'georefine'
georefine_db_password = 'georefine' #@TODO: read from node attributes or dbag.
georefine_db_connection = {
    :host => "localhost",
    :port => 5432,
    :username => 'postgres',
    :password => node['postgresql']['password']['postgres']
}

postgresql_database_user georefine_db_user do
    connection georefine_db_connection
    password georefine_db_password
    action :create
end

postgis_contrib_dir = "/usr/share/postgresql/#{node['postgresql']['version']}/contrib/postgis-1.5"
postgis_sql = "#{postgis_contrib_dir}/postgis.sql"
postgis_srs_sql = "#{postgis_contrib_dir}/spatial_ref_sys.sql"
execute 'spatialize db' do
    command "createlang plpgsql georefine; psql -d georefine -f #{postgis_sql}; psql -d georefine -f #{postgis_srs_sql}"
    user 'postgres'
    action :nothing
end

postgresql_database 'georefine' do
    connection georefine_db_connection
    owner georefine_db_user
    action :create
    notifies :run, resources(:execute => 'spatialize db')
end


# Setup app config.

# Setup apache config.


# Setup virtualenv.
