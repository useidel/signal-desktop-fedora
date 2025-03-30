# signal-desktop-fedora

A SPEC file for Signal-Desktop to create an RPM for fedora. 

The source of signal-desktop are here: [Signal-Desktop](https://github.com/signalapp/Signal-Desktop)

SPEC file inspired by [luminoso](https://copr.fedorainfracloud.org/coprs/luminoso/Signal-Desktop)

And if you want to build the RPMs on-premise you should visit [BarbossHack's Signal-Desktop-Fedora](https://github.com/BarbossHack/Signal-Desktop-Fedora)

The content of the SPEC file basically follows the instructions from [Reproducible Builds](https://github.com/signalapp/Signal-Desktop/tree/main/reproducible-builds). For that it requires internet access to install nodejs, nvm and pnpm with the required version. 


---

#### Might be worth checking out too ...

The files *getsources.sh* and *.github/workflows/rpmbuild_copr.yml* are used for automated RPM package builds using [Github Actions](https://github.com/useidel/signal-desktop-fedora/actions) and [Copr](https://copr.fedorainfracloud.org/coprs/useidel/signal-desktop/).

More generic information about the [Github Actions](https://github.com/features/actions) to [Copr](https://copr.fedorainfracloud.org/) connection can be found [here](https://github.com/useidel/copr-build-test).



