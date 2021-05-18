# signal-desktop-fedora

Some experiments with the SPEC file to create an RPM for fedora - basically about the patching of the source.

The source of signal-desktop are here: https://github.com/signalapp/Signal-Desktop

SPEC file inspired by: https://copr.fedorainfracloud.org/coprs/luminoso/Signal-Desktop/

The current build requires internet access and the additional repo https://rpm.nodesource.com/pub_14.x/fc/$releasever/$basearch

It is worth matching the version from nodesource with the one shipped by the fedora distribution.

Mainly the discussion between inline patches in the SPEC file or having them outsourced to patch files.

