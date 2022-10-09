# signal-desktop-fedora

Some experiments with the SPEC file to create an RPM for fedora - basically about the patching of the source.

The source of signal-desktop are here: [Signal-Desktop](https://github.com/signalapp/Signal-Desktop)

SPEC file inspired by: https://copr.fedorainfracloud.org/coprs/luminoso/Signal-Desktop/

The current build requires internet access and the additional repo https://rpm.nodesource.com/pub_16.x/fc/$releasever/$basearch

It is worth matching the version from nodesource with the one shipped by the fedora distribution.

---

#### Might be worth checking out too ...

The files *getsources.sh* and *.github/workflows/rpmbuild_copr.yml* are used for automated RPM package builds using [Github Actions](https://github.com/useidel/signal-desktop-fedora/actions) and [Copr](https://copr.fedorainfracloud.org/coprs/useidel/signal-desktop/).

More generic information about the [Github Actions](https://github.com/features/actions) to [Copr](https://copr.fedorainfracloud.org/) connection can be found [here](https://github.com/useidel/copr-build-test).



