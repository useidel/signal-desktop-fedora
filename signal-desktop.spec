Name:		signal-desktop
Version:	5.40.0
Release:	1%{?dist}
Summary:	Private messaging from your desktop
License:	GPLv3
URL:		https://github.com/signalapp/Signal-Desktop/

Source0:	https://github.com/signalapp/Signal-Desktop/archive/v%{version}.tar.gz
Patch0:		signal-desktop-expire-from-source-date-epoch.patch

#ExclusiveArch:	x86_64
BuildRequires: binutils, git, python2, gcc, gcc-c++, openssl-devel, bsdtar, jq, zlib, xz, nodejs, ca-certificates, git-lfs
%if 0%{?fedora} > 28
BuildRequires: python-unversioned-command
%endif
%if 0%{?fedora} > 29
BuildRequires: libxcrypt-compat
%endif
%if 0%{?fedora} > 31
BuildRequires: libxcrypt-compat, vips-devel
%endif
%if 0%{?el8}
BuildRequires: platform-python-devel, python3
%endif

%if 0%{?fedora} > 31
BuildRequires: yarnpkg
%else
BuildRequires: yarn
%endif

AutoReqProv: no
#AutoProv: no
Provides: signal-desktop
Requires: libnotify, libXtst, nss

%global __requires_exclude_from ^/%{_libdir}/%{name}/release/.*$
%define _build_id_links none

%description
Private messaging from your desktop

%prep
# https://bugzilla.redhat.com/show_bug.cgi?id=1793722
export SOURCE_DATE_EPOCH="$(date +"%s")"

# git-lfs hook needs to be installed for one of the dependencies
git lfs install

node --version
rm -rf Signal-Desktop-%{version}
tar xfz %{S:0}

pwd

cd Signal-Desktop-%{version}

# Allow higher Node versions
sed 's#"node": "#&>=#' -i package.json

# We can't read the release date from git so we use SOURCE_DATE_EPOCH instead
%patch0 -p0

npm config set python /usr/bin/python2
yarn install --ignore-engines

%build
# https://bugzilla.redhat.com/show_bug.cgi?id=1793722
export SOURCE_DATE_EPOCH="$(date +"%s")"
echo $SOURCE_DATE_EPOCH


cd %{_builddir}/Signal-Desktop-%{version} 

yarn generate
yarn build

%install

# Electron directory of the final build depends on the arch
%ifnarch x86_64
    %global PACKDIR linux-ia32-unpacked
%else
    %global PACKDIR linux-unpacked
%endif


# copy base files
install -dm755 %{buildroot}/%{_libdir}/%{name}
cp -a %{_builddir}/Signal-Desktop-%{version}/release/linux-unpacked/* %{buildroot}/%{_libdir}/%{name}

install -dm755 %{buildroot}%{_bindir}
ln -s %{_libdir}/%{name}/signal-desktop %{buildroot}%{_bindir}/signal-desktop

install -dm755 %{buildroot}%{_datadir}/applications/
# Changes from upstream:
# 1. Run signal WITH sandbox since it looks like there's no problems with fedora and friends
# 2. Use tray icon by default
# 3. Small fix for tray for Plasma users
cat << EOF > %{buildroot}%{_datadir}/applications/signal-desktop.desktop
[Desktop Entry]
Name=Signal
Exec=/usr/bin/signal-desktop --use-tray-icon %U
Terminal=false
Type=Application
Icon=signal-desktop
StartupWMClass=Signal
Comment=Private messaging from your desktop
MimeType=x-scheme-handler/sgnl;
Categories=Network;InstantMessaging;Chat;
EOF

for i in 16 24 32 48 64 128 256 512 1024; do
    install -dm755 %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/
    install -Dm 644 %{_builddir}/Signal-Desktop-%{version}/build/icons/png/${i}x${i}.png %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/%{name}.png
done

%files
%defattr(-,root,root)
%{_bindir}/*
%{_libdir}/*
%{_datadir}/*
 

%changelog
* Thu Apr 21 2022 Udo Seidel <udoseidel@gmx.de> 5.40.0-1
- Bug fixes including a fix to an issue that would sometimes make it difficult to click on menus.
- Thanks to our open source contributors @dsanders11 and @yusufsahinhamza for contributing to these improvements.

* Thu Apr 14 2022 Udo Seidel <udoseidel@gmx.de> 5.39.0-1
- You can now add people to groups using just their phone number.
- Your favorite contacts are now just a few keystrokes away. 
- Contact search now supports non-Latin alphabets like Cyrillic.

* Thu Apr 07 2022 Udo Seidel <udoseidel@gmx.de> 5.38.0-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.

* Fri Mar 25 2022 Udo Seidel <udoseidel@gmx.de> 5.36.0-1
- Quickly scanning that group chat? There's more room for more messages on the screen at once. We now group sender's messages together if they're close together in time.
- When you perform a Delete for Everyone you'll now see a progress spinner letting you know whether it's been successfully sent or not. If it fails for some reason, you'll be able to retry too!

* Thu Mar 10 2022 Udo Seidel <udoseidel@gmx.de> 5.35.0-1
- A new update system has been introduced and folks should start seeing smaller updates with the next update.
- Applications that use media keys rejoice! Signal no longer has a hold on them.
- Better font support for our Japanese friends.

* Sat Mar 05 2022 Udo Seidel <udoseidel@gmx.de> 5.34.0-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.
- Ever used Signal while on an unstable connection? You can worry no more - disappearing message timer changes and more will now be synced back once your Wi-Fi feels better again.

* Wed Feb 16 2022 Udo Seidel <udoseidel@gmx.de> 5.32.0-1
- and again trying to stay on top of the actual released version

* Thu Feb 10 2022 Udo Seidel <udoseidel@gmx.de> 5.31.0-1
- and trying to stay on top of the actual released version :-)

* Thu Feb 10 2022 Udo Seidel <udoseidel@gmx.de> 5.30.0-1
- catch-up with actual minor release

* Wed Jan 05 2022 Udo Seidel <udoseidel@gmx.de> 5.26.0-1
- catch-up with actual minor release

* Mon Nov 01 2021 Udo Seidel <udoseidel@gmx.de> 5.22.0-1
- boost to actual minor release

* Wed Oct 20 2021 Udo Seidel <udoseidel@gmx.de> 5.20.0-1
- boost to actual minor release

* Sat Oct 09 2021 Udo Seidel <udoseidel@gmx.de> 5.19.0-1
- boost to most recent minor release

* Wed Sep 29 2021 Udo Seidel <udoseidel@gmx.de> 5.17.2-1
- next minor release

* Mon Sep 13 2021 Udo Seidel <udoseidel@gmx.de> 5.17.1-1
- next minor release

* Thu Sep 09 2021 Udo Seidel <udoseidel@gmx.de> 5.16.0-1
- Guess what: jump to latest minor release

* Sat Aug 07 2021 Udo Seidel <udoseidel@gmx.de> 5.12.1-1
- And Again jump to latest minor release

* Thu Jul 29 2021 Udo Seidel <udoseidel@gmx.de> 5.11.0-1
- Again jump to latest minor release

* Fri Jul 09 2021 Udo Seidel <udoseidel@gmx.de> 5.8.0-1
- Again jump to latest minor release

* Sun Jun 06 2021 Udo Seidel <udoseidel@gmx.de> 5.4.0-1
- Jump to latest minor release
- remove of package.json patch

* Sun May 16 2021 Udo Seidel <udoseidel@gmx.de> 5.1.0-1
- Update to new minor release
- Remove openssl dynamic link patches
- Remove bundled binaries for other platforms

* Sat May 01 2021 Udo Seidel <udoseidel@gmx.de> 5.0.0-1
- Update to new major version

* Thu Feb 18 2021 Udo Seidel <udoseidel@gmx.de> 1.40.0-1
- update to new release

* Tue Jan 26 2021 Udo Seidel <udoseidel@gmx.de> 1.39.6-3
- patching outsourced from SPEC to patch files

* Mon Jan 25 2021 Udo Seidel <udoseidel@gmx.de> 1.39.6-2
- cleanup of spec file
- covering renaming of yarn package on fedora

* Fri Sep 25 2020 Guilherme Cardoso <gjc@ua.pt> 1.36.2-1
- Patch to remove fsevents from build, since it make build failing
in linux environments and is only needed for Apple MacOS users

* Mon Jul 27 2020 Guilherme Cardoso <gjc@ua.pt> 1.34.4-3
- Replaced 'requires' 'libappindicator' with 'libappindicator-gtk3'

* Sun Jun 21 2020 Guilherme Cardoso <gjc@ua.pt> 1.34.2-2
- Re-order %build and %prep steps
- Also manually build zkgroup nodemodule shared object on el7

* Tue Apr 28 2020 Guilherme Cardoso <gjc@ua.pt> 1.33.4-1
- Added workarounds for el8 copr build

* Tue Apr 7 2020 Guilherme Cardoso <gjc@ua.pt> 1.33.0-1
- Reordered patching and build flow
- Removed spellchecker directory patch for fedora 

* Sat Mar 14 2020 Guilherme Cardoso <gjc@ua.pt> 1.32.1-2
- Don't try to override XDG_CURRENT_DESKTOP anymore 

* Sat Feb 08 2020 Guilherme Cardoso <gjc@ua.pt> 1.30.1-3
- Fix spellchecker and audio player. Huge thank you to Christoph Schwille

* Fri Jan 24 2020 Guilherme Cardoso <gjc@ua.pt> 1.30.0-1
- Refactor spec file, since Signal no longer builds rpm file
- Fix package providing and requiring a lot of libraries
- Slimmed down instalation by deleting some build files present on release

* Mon Jan 20 2020 Guilherme Cardoso <gjc@ua.pt> 1.29.6-1
- Resync patches and build recipe from archlinux
- RPM spec build dependencies cleanup (ZaWertun)

* Thu Nov 14 2019 Guilherme Cardoso <gjc@ua.pt> 1.28.0-1
- Simplify changelog to include only major changes

* Fri Sep 6 2019 Guilherme Cardoso <gjc@ua.pt> 1.27.1-1
- Version bump
- Small adjustments to rpm spec file and its patches

* Sat Mar 30 2019 Guilherme Cardoso <gjc@ua.pt> 1.23.2-1
- Updated to dynamic eletron version, idea taken from
ArchLinux AUR Signal package (_installed_electron_version)

* Thu Jan 17 2019 Guilherme Cardoso <gjc@ua.pt> 1.20.0-2
- Version bump
- Updated patches from archlinux aur build
- Add depndencies for Fedora rawhide

* Wed Oct 31 2018 Guilherme Cardoso <gjc@ua.pt> 1.17.2-1
- Version bump
- Explicit nodejs dependency, which tries to solve the requirement of having nodejs LTS version 8
- Thanks clime for the help

* Mon Oct 22 2018 Guilherme Cardoso <gjc@ua.pt> 1.16.3-4
- Fix wrong this rpmspec version info

* Mon Oct 15 2018 Guilherme Cardoso <gjc@ua.pt> 1.16.2-3
- Workaround for KDE plasma Signal's tray icon
https://github.com/signalapp/Signal-Desktop/issues/1876

* Fri Oct 12 2018 Guilherme Cardoso <gjc@ua.pt> 1.16.2-2
- Patch to use tray icon

* Fri Aug 17 2018 Guilherme Cardoso <gjc@ua.pt> 1.15.5-2
- Try to patch to allow higher node versions for Fedora Rawhide
- Manual symlink

* Thu Aug 16 2018 Matthias Andree <mandree@FreeBSD.org> 1.15.5-1
- Shuffle things around a bit
- Add jq to build requisites
- tweak files section so it actually finds its inputs
- add node-gyp to developer dependencies only
- add -no-default-rc to yarn calls throughout

* Tue Aug 14 2018 Guilherme Cardoso <gjc@ua.pt> 1.15.4-1
- Version bump
- Build fixes arround embebed OpenSSL's from mandree and stemid
Link: https://github.com/signalapp/Signal-Desktop/issues/2634

* Wed May 02 2018 Guilherme Cardoso <gjc@ua.pt> 1.9.0-1
- Version bump
- Spec file cleanup

* Mon Apr 16 2018 Guilherme Cardoso <gjc@ua.pt> 1.7.1-4
- Added a few more yarn steps (check, lint)

* Mon Apr 16 2018 Guilherme Cardoso <gjc@ua.pt> 1.7.1-3
- Fix build. Requires 'yarn transpile'. Thanks spacekookie.
Ref: https://github.com/signalapp/Signal-Desktop/issues/2256

* Sat Apr 14 2018 Guilherme Cardoso <gjc@ua.pt> 1.7.1-2
- Remove patch lowering nodejs due to async problems
- Simplified BuildRequires

* Wed Apr 11 2018 Guilherme Cardoso <gjc@ua.pt> 1.6.1-2
- Fix desktop shortcut (thanks to bol for reporting)

* Tue Mar 13 2018 Guilherme Cardoso <gjc@ua.pt> 1.6.0-1
- Version bump
- Update project homepage url
- Patch to override nodejs version of Signal's sources

* Sun Feb 18 2018 Guilherme Cardoso <gjc@ua.pt> 1.3.0-2
- Build from sources instead of unpacking .deb release

* Mon Feb 05 2018 Guilherme Cardoso <gjc@ua.pt> 1.3.0-1
- Version bump
- Added missing dependencies from original deb package

* Thu Nov 02 2017 Richard Monk <richardmonk@gmail.com> 1.0.35-1
- Initial Packaging
