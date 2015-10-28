This is a beta version of mwm-making package.

It contains binaries compiled for Ubuntu 14.04 x64. They should work in later versions.
You would need Qt 5.3 and some other packages:

    sudo apt-get install libtbb2 libluabind0.9.1 liblua50 libstxxl1

After that, download pbf/o5m/bz2 and run (for A.pbf):

    DATA_PATH=data ./generate_mwm.sh A.pbf data/car.lua

It should produce A.mwm and A.mwm.routing, which you can put on your device into a MapsWithMe folder.
