#!/usr/bin/bash -x

PATH=/usr/bin:/usr/sbin/
export PATH

# This will setup the needed directory structure to build RPM packages
# please note that this will not happen in the $GITHUB_WORKSPACE 
# but in the RPMBUILD space instead
rpmdev-setuptree

# Get the version from the SPEC file
MYVER=`grep ^Version *.spec |awk '{print $2}'`

# copy the also needed patch file(s) to the RPMBUILD space
# again this is different from the $GITHUB_WORKSPACE
cp *.patch /github/home/rpmbuild/SOURCES

# Now download the sources to the correspoding RPMBUILD directory
cd /github/home/rpmbuild/SOURCES
wget -nd https://github.com/signalapp/Signal-Desktop/archive/refs/tags/v${MYVER}.tar.gz


