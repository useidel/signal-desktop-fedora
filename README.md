# signal-desktop-fedora

Some experiments with the SPEC file to create an RPM for fedora - basically about the patching of the source.

The source of signal-desktop are here: [Signal-Desktop](https://github.com/signalapp/Signal-Desktop)

SPEC file inspired by [luminoso](https://copr.fedorainfracloud.org/coprs/luminoso/Signal-Desktop)

And if you want to build the RPMs on-premise you should visit [BarbossHack's Signal-Desktop-Fedora](https://github.com/BarbossHack/Signal-Desktop-Fedora)

It basically follows the instructions from [How to compile Signal-Desktop for Fedora](https://github.com/michelamarie/fedora-signal/wiki/How-to-compile-Signal-Desktop-for-Fedora) but skips the installation of nvm (node Version Manager) and some follow-up steps because installs the needed npm version an external repo (see below). Also, it does not replace "deb" by "rpm" in the package.json file since this is not needed either.

The current build requires internet access and the additional repo https://rpm.nodesource.com/pub_20.x/nodistro/nodejs/$basearch

It is worth matching the version from nodesource with the one shipped by the fedora distribution.


---

#### Might be worth checking out too ...

The files *getsources.sh* and *.github/workflows/rpmbuild_copr.yml* are used for automated RPM package builds using [Github Actions](https://github.com/useidel/signal-desktop-fedora/actions) and [Copr](https://copr.fedorainfracloud.org/coprs/useidel/signal-desktop/).

More generic information about the [Github Actions](https://github.com/features/actions) to [Copr](https://copr.fedorainfracloud.org/) connection can be found [here](https://github.com/useidel/copr-build-test).



