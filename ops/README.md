The Maps.ME generator_tool must be built for the target OS (Ubuntu 18.04 LTS).

See instructions at https://github.com/mapsme/omim/blob/master/docs/INSTALL.md#maps-generator

```
sudo apt install cmake qt5-default
git clone --recursive --depth 1 https://github.com/mapsme/omim.git
./configure
omim/tools/unix/build_omim.sh -sr generator_tool
tar -cvzf omim-build-release.tgz ../omim-build-release
```
