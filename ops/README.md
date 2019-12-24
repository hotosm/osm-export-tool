# Export Tool Ops

Included here are complete instructions to run the Export Tool and Overpass API on Ubuntu 18.04 LTS. the `overpass` and `packer` directories include scripts to create base images on Azure or another cloud provider via [Packer](http://packer.io). If you are using another tool such as Docker, the scripts such as `packer/provision.sh` and configuration files like `nginx.conf` should also work, as long as you are using an Ubuntu 18.04 LTS base image.

## Azure

### Image creation 
Use this command to get your Azure CLIENT_ID and CLIENT_SECRET environment variables for [Packer](https://www.packer.io/docs/builders/azure-setup.html):
```
az ad sp create-for-rbac -n "Packer" --role contributor --scopes /subscriptions/<SUBSCRIPTION_ID>
```
The values in the `variables` section of `packer.json` may need to be modified to your specific Azure region and resource group. The images can then be created via `packer packer.json`.

### Launching an instance

1. Choose the created image in the Azure "Add virtual machine..." UI.
2. The instance must be assigned an existing Resource Group.
3. Choose an appropriate instance size. For the Overpass instance, at least 16 GB of RAM is recommended.
4. Set the login username e.g. `ubuntu` and add your SSH public key.
5. Open ports 22 and 80, additionally port 443 for the web application.
6. Create or attach data disks. About 400GB is necessary for the Overpass instance. 

## Post-launch instance setup

See [Overpass API/Installation](https://wiki.openstreetmap.org/wiki/Overpass_API/Installation)

1. Format the data disk and mount at `/data`.
2. 	* Modify `/etc/fstab` to auto-mount this device on boot.
	* Change /etc/nginx/nginx.conf to the file overpass/nginx.conf
	* Make sure all CGI scripts in /home/overpass/osm3s.../cgi_bin are executable.(chmod +x)
3. Set the owner of `data` to `overpass:overpass`.
4. Switch to the `overpass` user: `sudo su overpass`
5. Clone a copy of the Overpass data to `/data`: 
```
./download_clone.sh --db-dir=/data --source=http://dev.overpass-api.de/api_drolbr/ --meta=attic
```
Attic data is necessary for augmented diff support. This clone can take several hours.
5. Start the dispatcher
6. Start `fetch_osc_and_apply.sh`

## Web application Setup (part 1)

1. Assign a DNS A record such as `export.example.com` to your instance's IP.
2. Modify /etc/nginx.conf, changing the 2nd entry of server_name to `export.example.com`
3. Run `sudo certbot --nginx -d export.example.com` and follow the prompts to create and install an SSL certificate. When prompted, choose to redirect all HTTP traffic to HTTPS.
4. Add to the crontab `0 0,12 * * * /usr/bin/certbot renew` . This will renew the SSL certificate when it is about to expire. 

## Web application setup (part 2)

1. The export tool runs as the `exports` user. Change to that user: `sudo su exports`
2. Clone the repository to `/home/exports`
3. Create a virtualenv: `virtualenv /home/exports/venv --python=python3` and activate it: `source /home/exports/venv/activate`
4. Install Python dependencies: `CPLUS_INCLUDE_PATH=/usr/include/gdal C_INCLUDE_PATH=/usr/include/gdal pip install -r /home/exports/osm-export-tool/requirements.txt`
5. Compile the JavaScript frontend: `cd /home/exports/osm-export-tool/ui; yarn install; yarn run dist`
6. Copy static assets: `cd /home/exports/osm-export-tool/ && python manage.py collectstatic`
7. Either run database migrations on the empty `exports` db: `python manage.py migrate` or restore a database backup.
Examples of how to backup and restore the database:


	pg_dump -U exports exports > backup_091319.pgdump
	psql exports < backup_091319.pgdump

8. Modify the OAuth2 application with your hostname's `redirect_uris`

### Storage and Environment Variables

Provision a large (>300GB) disk for scratch space and downloads. [Azure Instructions](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/attach-disk-portal)

	sudo fdisk /dev/sdc # assuming disk is /dev/sdc, choose: n,p defaults, w
	sudo mkfs -t ext4 /dev/sdc1
	sudo mkdir /mnt/data
	sudo mount /dev/sdc1 /mnt/data
	sudo chown exports:exports /mnt/data

Determine the disk UUID with `sudo -i blkid` and add it to fstab to mount on boot:


	UUID=33333333-3b3b-3c3c-3d3d-3e3e3e3e3e3e   /mnt/data   ext4   defaults,nofail   1   2
	
### Restarting the worker

It's possible that certain jobs or problems with the exporting utilities causes jobs to hang, in which case a CloudWatch alarm will alert about many enqueued jobs. The worker process can be restarted via:

`sudo service worker-ondemand restart`
or `sudo service worker-scheduled restart`

### Logging

Systemd's `journalctl` should be used to view logs. To view worker logs, run: `journalctl -fu
worker-ondemand` or `worker-scheduled`.

### Backups

TODO `docker.postgresql-backup.{service,timer}` define a unit that runs daily to back the database up to
S3. To check its schedule, run `systemctl list-timers`.

### Pre-compiled libraries

The Maps.ME generator_tool must be built for the target OS (Ubuntu 18.04 LTS).

See instructions at https://github.com/mapsme/omim/blob/master/docs/INSTALL.md#maps-generator

```
sudo apt install cmake qt5-default
git clone --recursive --depth 1 https://github.com/mapsme/omim.git
./configure
omim/tools/unix/build_omim.sh -sr generator_tool
tar -cvzf omim-build-release.tgz ../omim-build-release
```
