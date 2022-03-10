# signal-desktop-fedora

Some experiments with the SPEC file to create an RPM for fedora - basically about the patching of the source.

The source of signal-desktop are here: https://github.com/signalapp/Signal-Desktop

SPEC file inspired by: https://copr.fedorainfracloud.org/coprs/luminoso/Signal-Desktop/

The current build requires internet access and the additional repo https://rpm.nodesource.com/pub_16.x/fc/$releasever/$basearch
Attention: at the moment there are no node packages for fedora releases beyond version 35.

It looks like Fedora versions below 35 do not work with signal-desktop of version above 30.

It is worth matching the version from nodesource with the one shipped by the fedora distribution.

