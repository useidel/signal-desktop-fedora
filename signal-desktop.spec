Name:		signal-desktop
Version:	7.18.0
Release:	1%{?dist}
Summary:	Private messaging from your desktop
License:	GPLv3
URL:		https://github.com/signalapp/Signal-Desktop/

Source0:	https://github.com/signalapp/Signal-Desktop/archive/v%{version}.tar.gz

BuildRequires: binutils git python2 gcc gcc-c++ openssl-devel bsdtar jq zlib xz nodejs >= 20.15.0 ca-certificates git-lfs ruby-devel
%if 0%{?fedora} > 28
BuildRequires: python-unversioned-command
%endif
%if 0%{?fedora} > 29
BuildRequires: libxcrypt-compat
%endif
%if 0%{?fedora} > 31
BuildRequires: libxcrypt-compat vips-devel
%endif
%if 0%{?el8}
BuildRequires: platform-python-devel python3
%endif

%if 0%{?fedora} > 31
BuildRequires: yarnpkg
%else
BuildRequires: yarn 
%endif

%if 0%{?fedora} > 35
BuildRequires: npm 
%endif

# new for AARCH64 builds
%ifarch aarch64
BuildRequires: rubygems, rubygem-json
%endif

AutoReqProv: no
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

cd Signal-Desktop-%{version}

# Allow higher Node versions
sed 's#"node": "#&>=#' -i package.json

# new for AARCH64 builds
# https://github.com/electron-userland/electron-builder-binaries/issues/49#issuecomment-1100804486
%ifarch aarch64
    # make sure that fpm binary is in PATH
    # need to strip some componentes from BUILDDIR
    FPMPATH=`dirname %{_builddir}`
    FPMPATH=`dirname $FPMPATH`
    PATH=$PATH:$FPMPATH/bin
# handle corner case where we need /builddir/bin on top of /buildir/build/bin
    FPMPATH=`dirname $FPMPATH`
    PATH=$PATH:$FPMPATH/bin
    export PATH
    gem install fpm
%endif

#
YARNCPATH=`dirname %{_builddir}`
YARNCPATH=`dirname $YARNCPATH`
mkdir -p $YARNCPATH/.config/yarn/global/
cp .yarnclean $YARNCPATH/.config/yarn/global/
yarn --c
yarn install --frozen-lockfileyarn

%build
# https://bugzilla.redhat.com/show_bug.cgi?id=1793722
export SOURCE_DATE_EPOCH="$(date +"%s")"
echo $SOURCE_DATE_EPOCH

# https://github.com/electron-userland/electron-builder-binaries/issues/49#issuecomment-1100804486
%ifarch aarch64
    export USE_SYSTEM_FPM=true
    # make sure that fpm binary is in PATH
    # need to strip some componentes from BUILDDIR
    FPMPATH=`dirname %{_builddir}`
    FPMPATH=`dirname $FPMPATH`
    FPMPATH=$FPMPATH/bin
    PATH=$PATH:$FPMPATH
    export PATH
%endif

cd %{_builddir}/Signal-Desktop-%{version} 

yarn generate
yarn build-release

%install

# Electron directory of the final build depends on the arch
%ifnarch x86_64
    %global PACKDIR linux-ia32-unpacked
%else
    %global PACKDIR linux-unpacked
%endif

# new for AARCH64 builds
%ifarch aarch64
    %global PACKDIR linux-arm64-unpacked
%endif

# copy base files
install -dm755 %{buildroot}/%{_libdir}/%{name}
cp -a %{_builddir}/Signal-Desktop-%{version}/release/%{PACKDIR}/* %{buildroot}/%{_libdir}/%{name}

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
* Thu Aug 01 2024 Udo Seidel <udoseidel@gmx.de> 7.18.0-1
- A quick goodbye is sometimes easier than a slow farewell, so we sped up the process of deleting large message threads.

* Sat Jul 27 2024 Udo Seidel <udoseidel@gmx.de> 7.17.0-3
- added logic to handle corner case for fpm on AARCH64

* Fri Jul 26 2024 Udo Seidel <udoseidel@gmx.de> 7.17.0-2
- nodejs >=20.15.0 is required (not shipped by fedora -> repo https://rpm.nodesource.com/ needed)

* Thu Jul 25 2024 Udo Seidel <udoseidel@gmx.de> 7.17.0-1
- We wanted things to be slicker and quicker for sticker clickers, so we fixed a bug that sometimes prevented Signal from launching the sticker viewer if you tried to open a sticker pack link while the app was closed. 

* Wed Jul 17 2024 Udo Seidel <udoseidel@gmx.de> 7.16.0-1
- We fixed a bug that prevented the button to minimize a call from appearing while that call was reconnecting. Now you don't need to feel disconnected from previous chats even if the internet is feeling disconnected.

* Wed Jul 03 2024 Udo Seidel <udoseidel@gmx.de> 7.15.0-1
- Now you can forward contact cards that were sent from a mobile device. Share the take-out number for your favorite restaurant without taking out your phone.
- New support for high-resolution "jumbomoji" adds larger-than-life detail to large emoji, especially on big screens with small pixels.
- We also updated the Sticker Creator to support the latest Emoji, so today's stickers are no longer stuck with yesterday's Unicode standard.

* Thu Jun 27 2024 Udo Seidel <udoseidel@gmx.de> 7.14.0-1
- If you're tired of losing your voice, we fixed a bug where switching to another chat or application while recording a voice message could cause that message to disappear. In-progress voice messages are now saved as drafts so you can review and send them when you return to the chat.

* Thu Jun 20 2024 Udo Seidel <udoseidel@gmx.de> 7.13.0-1
- We fixed a bug that displayed images with the wrong aspect ratio if you resized the Signal Desktop window while viewing someone's profile picture. The people you love should only look squeezed if you are giving them a hug.
- This update also improves the display of quoted replies in RTL languages.

* Wed Jun 12 2024 Udo Seidel <udoseidel@gmx.de> 7.12.0-1
- Raise your hand if you've been looking for another way to communicate during group calls. The new Raise Hand feature is a simple way to get someone's attention, ask a question, or unanimously vote for a group proposal when your friend asks "all those in favor?"
- We modified the keyboard shortcut for sending a voice note to Ctrl/Cmd+Shift+Y so that it no longer conflicts with the "Paste and Match Style" shortcut on Windows and Linux.
- We broke up with a bug in the crop tool, so now it's easier and more intuitive to cut your ex (or anything else) out of the picture.

* Tue Jun 04 2024 Udo Seidel <udoseidel@gmx.de> 7.11.1-1
- see below

* Thu May 30 2024 Udo Seidel <udoseidel@gmx.de> 7.11.0-1
- We fixed a rendering bug that caused the contacts icon to smash itself right next to the contact's name while viewing the list of participants in a group call. You're probably really close to your contacts, but sometimes you (and the Signal Desktop user interface) both need a little space.

* Wed May 22 2024 Udo Seidel <udoseidel@gmx.de> 7.10.0-2
- Added ruby-devel to build requirements

* Wed May 22 2024 Udo Seidel <udoseidel@gmx.de> 7.10.0-1
- Handful of bug fixes to keep your app running smoothly. More exciting changes on the horizon!

* Wed May 15 2024 Udo Seidel <udoseidel@gmx.de> 7.9.0-1
- Additional small tweaks, bug fixes, and performance enhancements. Thanks for using Signal!

* Wed May 08 2024 Udo Seidel <udoseidel@gmx.de> 7.8.0-1
- Now you can react with any emoji during a Signal call. Smile even if your camera is off, share a heart if you love what you're hearing, or vote for sushi instead of pizza without saying a word. And you'll even see an animation of everyone's emojional outburst if enough people in the call react with the same emoji all at once.

* Wed May 01 2024 Udo Seidel <udoseidel@gmx.de> 7.7.0-1
- Tweaks, bug fixes, and performance enhancements. Keep on texting, calling, and video chatting as usual.

* Fri Apr 26 2024 Udo Seidel <udoseidel@gmx.de> 7.6.0-1
- Small tweaks, bug fixes, and performance enhancements. Thanks for using Signal!

* Thu Apr 18 2024 Udo Seidel <udoseidel@gmx.de> 7.5.1-1
- see below

* Tue Apr 16 2024 Udo Seidel <udoseidel@gmx.de> 7.5.0-1
- We added support for custom nicknames and notes for anyone you're chatting with on Signal, even if they aren't in your system contacts. Whether you're adding the missing letters in a lazy friend's profile name, or a reminder about where you met, notes and nicknames provide a convenient and secure way to jot down additional details about your Signal Connections — and they're end-to-end encrypted and protected by your Signal PIN so they can be securely restored if you lose your phone too.
- Now you can minimize Signal to your system tray on Linux. If your taskbar is the right shade of gray, it’s like your messages are waiting for you on a silver platter.
- For users on Windows, this update re-enables support for detailed unread message counts on the Signal icon. Say goodbye to “9+” because now the icon goes to 11 (or higher).

* Fri Mar 29 2024 Udo Seidel <udoseidel@gmx.de> 7.4.0-1
- This update clears out a few bugs just in time for spring cleaning, including more consistent conversation sort logic and improved behavior if the app encounters DNS lookup timeouts due to poor network connectivity.

* Fri Mar 22 2024 Udo Seidel <udoseidel@gmx.de> 7.3.1-1
- see below

* Thu Mar 21 2024 Udo Seidel <udoseidel@gmx.de> 7.3.0-1
- Now you can clear missed calls on your phone and the badge on the calls tab in Signal Desktop will be updated too.
- We also redesigned the badge count indicator on Windows. Now the color in the taskbar matches the color in the system tray. Fashion is all about coordination, and a little pop of red is a perfect look for spring.

* Tue Mar 19 2024 Udo Seidel <udoseidel@gmx.de> 7.2.1-1
- see below

* Thu Mar 14 2024 Udo Seidel <udoseidel@gmx.de> 7.2.0-1
- Thanks to the performance improvements in this release, opening large group chats is faster than ever. If you're in a group with several hundred people that likes to debate the existence of parallel universes, you now live in a timeline where it takes a lot less time to show the timeline of people talking about timelines.

* Thu Mar 07 2024 Udo Seidel <udoseidel@gmx.de> 7.1.1-1
- see below

* Thu Mar 07 2024 Udo Seidel <udoseidel@gmx.de> 7.1.0-1
- This update enables support for all of the new emoji characters in Emoji version 15.1. People keep asking us what our favorite new emoji is, but answering that question is a “lime” we won't cross.

* Thu Feb 29 2024 Udo Seidel <udoseidel@gmx.de> 7.0.0-1
- Your phone number will no longer be visible to anyone on the latest version of Signal unless they have it saved in their phone’s contacts. You can change this in Settings.
- You can now set and share an optional username to let people chat with you without giving them your phone number.
- A new privacy setting lets you control who can find you by your phone number on Signal.

* Thu Feb 22 2024 Udo Seidel <udoseidel@gmx.de> 6.48.1-1
- see below

* Tue Feb 20 2024 Udo Seidel <udoseidel@gmx.de> 6.48.0-1
- Video and audio playback will now pause whenever the Signal window is closed and minimized in the system tray. If you’re looking for silence, X marks the spot.  
- By popular demand, emoticons like “:-)” now automatically become emoji like “🙂” — but if this makes you “:-(“ you can disable this feature in the “Chats” section of your Signal Desktop settings

* Thu Feb 15 2024 Udo Seidel <udoseidel@gmx.de> 6.47.1-1
- see version 6.47.0-1

* Thu Feb 08 2024 Udo Seidel <udoseidel@gmx.de> 6.47.0-1
- If you spend a lot of time trying to pick out the perfect emoji reaction for every situation, you'll be to know that we fixed a bug with typing indicators that sometimes caused the emoji selection box to disappear while you were in the middle of pondering your choices.
- Signal will now match your selected title bar color on Microsoft Windows. When all of your windows in Windows look the same, that's a common theme.

* Wed Jan 31 2024 Udo Seidel <udoseidel@gmx.de> 6.46.0-1
- The default fonts for Urdu have been updated for improved readability when that language is selected (Signal Settings > Appearance > Language). Thanks, @asakpke [github.com]!

* Wed Jan 24 2024 Udo Seidel <udoseidel@gmx.de> 6.45.0-1
- Now you can optionally turn emoticons into emoji. If you want to “🙂” whenever you type “:-)”, you can enable this feature in the “Chats” section of your Signal Desktop settings.  
- A new keyboard shortcut (Ctrl+s/Cmd+s) helps you quickly save pictures and videos from the media viewer.
- It’s too bad that we already made a New Year's Resolution joke in the release notes for the last update, because we just increased the maximum resolution for screen sharing during Signal video calls. Our new resolution is to avoid any resolution puns until 2025.
- Thanks to @dasois [github.com] and @pelya [github.com] for their contributions to this release!  

* Thu Jan 18 2024 Udo Seidel <udoseidel@gmx.de> 6.44.1-1
- see previous

* Thu Jan 11 2024 Udo Seidel <udoseidel@gmx.de> 6.44.0-1
- If resolving a few small bugs counts as a New Year’s resolution, then 2024 is off to a fantastic start.
- Region-neutral font fallback logic improves how CJK characters are displayed across different locales.
- Thanks to @0o001 [github.com], @hackerbirds [github.com], @rschiang [github.com], @vijithassar [github.com], and @yaslama [github.com] for their contributions to this release!

* Tue Jan 09 2024 Udo Seidel <udoseidel@gmx.de> 6.43.2-1
- see previous

* Fri Jan 05 2024 Udo Seidel <udoseidel@gmx.de> 6.43.1-1
 -see previous

* Thu Jan 04 2024 Udo Seidel <udoseidel@gmx.de> 6.43.0-1
- Turn a missed call into something that won't be missed. Now you can right-click on any call event and delete it from a chat.
- The default font for Persian has been updated to Vazirmatn to improve readability when that language is selected (Signal Settings > Appearance > Language). Thanks, @MahdiNazemi!
- The playback speed indicators in voice messages have a slightly new look. X marks the spot. Thanks, @Shrinks99!
- We would also like to thank @NetSysFire, @timjamello, and @u32i64 for their contributions to this release.

* Sat Dec 23 2023 Udo Seidel <udoseidel@gmx.de> 6.42.1-1
- We fixed a bug that displayed quoted replies to videos as though they were quoted replies to photos, even though every video is really just a sequence of photos if you think about it.
- Thanks to @qauff and @wyvurn-h4x3r for their help with this release.

* Thu Dec 14 2023 Udo Seidel <udoseidel@gmx.de> 6.42.0-1
- We fixed a bug that displayed quoted replies to videos as though they were quoted replies to photos, even though every video is really just a sequence of photos if you think about it.
- Thanks to @qauff [github.com] and @wyvurn-h4x3r [github.com] for their help with this release.

* Thu Nov 30 2023 Udo Seidel <udoseidel@gmx.de> 6.41.0-1
- We fixed the transition animation for video tiles when someone joins or leaves a group call. When you see a friend's face slide into view, that's a social movement.
-  Now you can click on a profile photo or group avatar in the chat header to quickly access chat settings or view any unseen stories from that chat. Thanks, @bhaskarraksahb [github.com]!

* Thu Nov 30 2023 Udo Seidel <udoseidel@gmx.de> 6.40.0-1
- Now you can change your selected language in Signal without changing your system settings (Signal Settings > Appearance > Language).
- We fixed a brief delay that sometimes occurred while joining a call lobby on macOS devices, which should get rid of at least one excuse

* Wed Nov 22 2023 Udo Seidel <udoseidel@gmx.de> 6.39.1-1
- Now you can change your selected language in Signal without changing your system settings (Signal Settings > Appearance > Language).
- We fixed a brief delay that sometimes occurred while joining a call lobby on macOS devices, which should get rid of at least one excuse
    for being a half-second late to the meeting.

* Thu Nov 16 2023 Udo Seidel <udoseidel@gmx.de> 6.39.0-1
- Now you can change your selected language in Signal without changing your system settings (Signal Settings > Appearance > Language).
- We fixed a brief delay that sometimes occurred while joining a call lobby on macOS devices, which should get rid of at least one excuse for being a half-second late to the meeting.

* Thu Nov 09 2023 Udo Seidel <udoseidel@gmx.de> 6.38.0-1
- This release includes an updated design for Signal voice and video calls. Now the calling user interface will still look fantastic even if your camera isn't on and you can't stare at your own beautiful reflection.

    name in the contact list on the New Chat screen and select "Remove."
* Thu Nov 02 2023 Udo Seidel <udoseidel@gmx.de> 6.37.0-1
- We've added a new way to keep your Signal contacts nice and tidy. This Halloween season, remove the ghost of an old contact. Just click on the three dots next to their
    name in the contact list on the New Chat screen and select "Remove."

* Wed Oct 25 2023 Udo Seidel <udoseidel@gmx.de> 6.36.0-1
- We updated the user interface to better indicate when a group video call is reconnecting. Now you'll see blurred thumbnails instead of what used to look like an elaborate prank where everyone pretended to freeze at the same time.  
- The system tray icon will no longer appear pixelated on Ubuntu Linux, unless you've managed to get Ubuntu Linux running on an old smart refrigerator with a low-res screen.

* Fri Oct 20 2023 Udo Seidel <udoseidel@gmx.de> 6.35.0-1
- We told ourselves that we would never do this, that we wouldn't be like the other apps with their lazy release notes, but this update really does include "bug fixes
and UX improvements."

* Mon Oct 16 2023 Udo Seidel <udoseidel@gmx.de> 6.34.1-1
- Typing indicators in group chats will now display multiple profile pictures if more than one person is typing. James Cameron convinced us that we didn't need to stop after one avatar.
- Now you can right-click on any sent message or press the up arrow on your keyboard to edit what you just said! Fix a tpyo, include the missing ingredient in grandma's chocolate chip cookie recipe, or add the punchline to a joke if you hit the send button too quickly. The choice is yours. Messages will always show when they have been edited, and you can click on the "Edited" indicator to see the full edit history for any edited messages. Update the past in the present to prevent future confusion today!

* Thu Oct 12 2023 Udo Seidel <udoseidel@gmx.de> 6.34.0-1
- Typing indicators in group chats will now display multiple profile pictures if more than one person is typing. James Cameron convinced us that we didn't need to stop after one avatar.
- Now you can right-click on any sent message or press the up arrow on your keyboard to edit what you just said! Fix a tpyo, include the missing ingredient in grandma's chocolate chip cookie recipe, or add the punchline to a joke if you hit the send button too quickly. The choice is yours. Messages will always show when they have been edited, and you can click on the "Edited" indicator to see the full edit history for any edited messages. Update the past in the present to prevent future confusion today!

* Fri Oct 06 2023 Udo Seidel <udoseidel@gmx.de> 6.33.0-1
- Now you can edit a message with a right click after it has been sent! Fix a tpyo, include the missing ingredient in grandma's chocolate chip cookie recipe, or add the punchline to a joke if you hit the send button too quickly. The choice is yours. Messages will always show when they have been edited, and you can click on the "Edited" indicator to see the full edit history for any edited messages. Update the past in the present to prevent future confusion today!

* Mon Oct 02 2023 Udo Seidel <udoseidel@gmx.de> 6.32.0-2
- update SPEC file to work around the missing yarnclean file issue on copr

* Fri Sep 29 2023 Udo Seidel <udoseidel@gmx.de> 6.32.0-1
- If you say "media editor" five times fast, it starts to sound like "mediator" — but the new media editor is so much easier to use that you'll no longer feel like you need a mediator to settle a fight between you and the crop tool.
- Sometimes the right reply can really help you get to the bottom of what people are saying, and now Signal will automatically scroll to what you just said whenever you send a message in a chat.


* Thu Sep 21 2023 Udo Seidel <udoseidel@gmx.de> 6.31.0-1
- This update fixes a handful of bugs, including one that caused the main Signal window to go blank if you viewed a debug log in full-screen mode on macOS. Seeing a completely Light or completely Dark window is arguably the purest possible expression of the Light Theme and Dark Theme, but we ultimately decided that the app is easier to use when you can see the interface too.

* Wed Sep 13 2023 Udo Seidel <udoseidel@gmx.de> 6.30.2-1
- Keep tabs on your calls with the new calls tab. Start a new call or return a call that you missed without having to find the corresponding chat. Now you can say hello with your voice without also saying goodbye to the unread marker for messages in that thread.

* Thu Sep 07 2023 Udo Seidel <udoseidel@gmx.de> 6.30.1-1
- Keep tabs on your calls with the new calls tab. Start a new call or return a call that you missed without having to find the corresponding chat. Now you can say hello with your voice without also saying goodbye to the unread marker for messages in that thread.

* Wed Sep 06 2023 Udo Seidel <udoseidel@gmx.de> 6.30.0-1
- Keep tabs on your calls with the new calls tab. Start a new call or return a call that you missed without having to find the corresponding chat. Now you can say hello with your voice without also saying goodbye to the unread marker for messages in that thread.

* Thu Aug 24 2023 Udo Seidel <udoseidel@gmx.de> 6.29.1-3
- cosmetic change related to previous fix and to cover misleading error message in prep phase

* Thu Aug 24 2023 Udo Seidel <udoseidel@gmx.de> 6.29.1-2
- fixed problem fpm not in PATH on AARCH64

* Thu Aug 24 2023 Udo Seidel <udoseidel@gmx.de> 6.29.1-1
- The Chat Color customization screen is now displayed correctly across different languages and selected locales.
- We improved notification support on Windows. If you don't click on a notification when it first arrives, the latest missed notification will appear in the Windows Notification Center. Clicking on that notification will now jump directly to that chat. We'd like to thank Julien Richard for their feedback.

* Tue Aug 22 2023 Udo Seidel <udoseidel@gmx.de> 6.29.0-1
- The Chat Color customization screen is now displayed correctly across different languages and selected locales.
- We improved notification support on Windows. If you don't click on a notification when it first arrives, the latest missed notification will appear in the Windows Notification Center. Clicking on that notification will now jump directly to that chat. We'd like to thank Julien Richard for their feedback.

* Wed Aug 09 2023 Udo Seidel <udoseidel@gmx.de> 6.28.0-1
- We modified the notification icons that appear for group updates, like when someone new joins a group. These icons help improve legibility, especially if you live within the darkness of the Dark Theme. The previous icons merely adopted the dark. The new icons were born in it, molded by it.

* Tue Aug 01 2023 Udo Seidel <udoseidel@gmx.de> 6.27.1-1
- This update includes a few improvements for voice and video calls, and some minor documentation updates (thanks, @vijithassar).

* Tue Aug 01 2023 Udo Seidel <udoseidel@gmx.de> 6.27.0-1
- This update includes a few improvements for voice and video calls, and some minor documentation updates (thanks, @vijithassar).

* Mon Jul 24 2023 Udo Seidel <udoseidel@gmx.de> 6.26.0-2
- fixed wrong date format in SPEC file

* Thu Jul 20 2023 Udo Seidel <udoseidel@gmx.de> 6.26.0-1
- Diacritics (such as accent marks) are now supported in @ mentions, so you can remind Aristotélēs to answer your philosophy question in the "Ancient Greek Time Travellers" group chat.
- Three cheers for triple-click text selection improvements. Thanks, @nrayburn-tech [github.com]!

* Fri Jul 14 2023 Udo Seidel <udoseidel@gmx.de> 6.25.0-1
- Now that the calling and conversation headers are draggable, repositioning your Signal window won't be such a drag.

* Thu Jul 06 2023 Udo Seidel <udoseidel@gmx.de> 6.24.0-1
- Now you can search your @ mentions too. "Thanks for adding this feature," you might say. "Don't mention it," we'll reply.

* Thu Jun 29 2023 Udo Seidel <udoseidel@gmx.de> 6.23.0-1
- In addition to a small assortment of bug fixes, this release also incorporates developer documentation updates (thanks, @d108!) and some design improvements to the message forwarding interface (thanks, @hackerbirds!).

* Thu Jun 22 2023 Udo Seidel <udoseidel@gmx.de> 6.22.0-1
- Format text in your messages by selecting any text in the message composition field. Make a bold statement that's actually bold, send M. Night Shyamalan a twist ending with a spoiler effect, emphasize a name by writing "Alex" in italics, put a line through a rejected dinner idea with strikethrough, or share code in monospace.
- We added support for the latest emoji characters, so now you can express your excitement with "Shaking Face" (🫨) or react with a "Pea Pod" (🫛) when someone asks you how close you are to your friends.


* Thu Jun 15 2023 Udo Seidel <udoseidel@gmx.de> 6.21.0-1
- Get a better look at yourself while a 1-on-1 call is ringing. Individual video calls now use the same full-screen view that previously only appeared at the beginning of a new group call. When it comes to being consistent, we try to be persistent (not resistant) and now the discrepancy is nonexistent because these things are no longer different.
-  We'd also like to express our appreciation to @complexspaces for their help and feedback while working on this release.

* Fri Jun 09 2023 Udo Seidel <udoseidel@gmx.de> 6.20.2-1

* Wed Jun 07 2023 Udo Seidel <udoseidel@gmx.de> 6.20.1-1
- If someone mentions you in a chat (like @ Your Name Goes Here), now you can quickly scroll to that mention and read all of the wonderful things that they said about you. You’re simply the best.

* Thu Jun 01 2023 Udo Seidel <udoseidel@gmx.de> 6.20.0-1
- If someone mentions you in a chat (like @ Your Name Goes Here), now you can quickly scroll to that mention and read all of the wonderful things that they said about you. You’re simply the best.

* Thu May 25 2023 Udo Seidel <udoseidel@gmx.de> 6.19.0-1
- Silence isn’t always golden, but it does have a new icon. We updated the Camera and Mute buttons in voice and video calls so it’s even easier to see when they are enabled or disabled.
- Localization improvements, and better handling of right-to-left languages in the message composition field. Thanks, @sha-265!
- If you are on a version of Windows before Windows 10, or a version of Ubuntu before 20.04 LTS, you will need to update your operating system to continue using Signal: https://support.signal.org/hc/articles/5109141421850-Supporting-Older-Operating-Systems 

* Tue May 23 2023 Udo Seidel <udoseidel@gmx.de> 6.18.1-1
- We've added additional translations for certain UI strings 

* Thu May 18 2023 Udo Seidel <udoseidel@gmx.de> 6.18.0-1
-  Use the "Navigate by section" keyboard shortcuts (⌘/Ctrl+T & ⌘/Ctrl+F6) to quickly move between different areas of the app. It's like a - superhero version of the Tab key that can fly further and faster than its mild-mannered alter ego.  
- We added support for optional message sounds so that you can also hear notifications for sent and received messages while a chat is - open (Settings > Notifications).
- Jump to the latest unread message in a chat (⌘/Ctrl+J) without touching the mouse or helping the touchpad live up to its name.
- Updated icons give the app a fresh look and help improve legibility. There's a new "Copy text" option in the triple-dot menu too. Thanks, @yusufsahinhamza!

* Fri May 12 2023 Udo Seidel <udoseidel@gmx.de> 6.17.1-1
- see previous release

* Tue May 09 2023 Udo Seidel <udoseidel@gmx.de> 6.17.0-1
- Improved support for right-to-left (RTL) languages.
- Locales are now matched based on your system preferences. This should result in better default behavior when multiple languages are configured.
- This release additionally (a10y) introduces several accessibility (a11y) enhancements and bug fixes, and we affectionately (a12y) would like to thank the community for their feedback and suggestions.


* Wed Apr 26 2023 Udo Seidel <udoseidel@gmx.de> 6.16.0-1
- Hard at work fixing bugs and making other performance improvements to keep the app running smoothly for you.

* Thu Apr 20 2023 Udo Seidel <udoseidel@gmx.de> 6.15.0-1
- The “Delete for everyone” option is now also available when multiple messages have been selected. Sometimes the road to a successful message is paved with “This message was deleted.”

* Wed Apr 12 2023 Udo Seidel <udoseidel@gmx.de> 6.14.0-1
- Tweaks, bug fixes, and performance enhancements. Keep on texting, calling, and video chatting as usual.

* Thu Apr 06 2023 Udo Seidel <udoseidel@gmx.de> 6.13.0-1
- Progress report: The new progress bar is ready. Quickly see more information about the loading process whenever you launch Signal Desktop.
- Theme preferences now also apply to the checkboxes in Signal Settings. Thanks to @rakleed on GitHub for helping us check "More fully embrace darkness in the dark theme" off of our TODO list.

* Tue Apr 04 2023 Udo Seidel <udoseidel@gmx.de> 6.12.0-4
- switched to use the fedora shipped npm and not the one from https://rpm.nodesource.com/pub_16.x/fc/$releasever/$basearch

* Sun Apr 02 2023 Udo Seidel <udoseidel@gmx.de> 6.12.0-3
- small clean-up

* Sat Apr 01 2023 Udo Seidel <udoseidel@gmx.de> 6.12.0-2
- enabled build for AARCH64 (https://github.com/signalapp/Signal-Desktop/issues/4530)

* Thu Mar 30 2023 Udo Seidel <udoseidel@gmx.de> 6.12.0-1
- Now you can select multiple messages and forward or delete them all at once.
- We updated the Sticker Creator with a few design tweaks and added some helpful tips for aspiring sticker artists. The Sticker Creator now opens in your web browser, which makes Signal Desktop a little smaller and leaves a bit more room on your hard drive for all of your favorite sticker packs.

* Thu Mar 23 2023 Udo Seidel <udoseidel@gmx.de> 6.11.0-1
- Start talking to yourself even faster with a new icon that makes the “Note to Self” chat easier to find. Thanks to @hackerbirds on GitHub for their contribution.

* Fri Mar 17 2023 Udo Seidel <udoseidel@gmx.de> 6.10.1-1
- same as 6.10.0-1

* Thu Mar 16 2023 Udo Seidel <udoseidel@gmx.de> 6.10.0-1
-  Click on any picture or video and use the new Forward and Backward buttons in the media viewer to take a visual walk down memory lane.
-  Voice messages are now saved as drafts if you switch to another chat while a recording is in progress.
-  Sending a sticker no longer causes draft text to get cleared. Thanks, @lamemakes [github.com]!
-  We'd also like to thank @norstbox [github.com] for bringing the conversation search bar icons back into alignment.

* Fri Mar 10 2023 Udo Seidel <udoseidel@gmx.de> 6.9.0-1
- Quickly see who is speaking during group calls with a new highlight feature that shows you where to look. If it's your turn to speak, you'll need to look within.
- Have the time of your life with several stickers in the media editor that let you add stylized time decorations on outgoing images.
- Use the voice notes mini player to continue listening to long messages even after you switch to a different chat.

* Thu Mar 02 2023 Udo Seidel <udoseidel@gmx.de> 6.8.0-1
- ou wouldn't download a car, but now when you download an MP3 voice note it will be saved with the proper file extension.
- Quickly begin typing a message after attaching a file, or just hit Enter/Return to send the file without any extra clicks. Thanks, @zyphlar!
- The send button in the large composition view has been brought into alignment. Thanks, @hackerbirds!
- If you are the only person in a group (so far) and you attempt to begin a group call, now you can join the call and start talking to yourself right away instead of waiting for the call to ring. Thanks, @lamemakes!

* Wed Feb 22 2023 Udo Seidel <udoseidel@gmx.de> 6.7.0-1
- Additional small tweaks, bug fixes, and assorted plans for the future.

* Thu Feb 16 2023 Udo Seidel <udoseidel@gmx.de> 6.6.0-1
- Hard at work fixing bugs and making other performance improvements to keep the app running smoothly for you.

* Sat Feb 11 2023 Udo Seidel <udoseidel@gmx.de> 6.5.1-1
- We fixed a rare bug that could prevent the app from launching correctly. If Signal started immediately crashing after the last update, you can reinstall this version without losing any of your message history. We sincerely apologize for the inconvenience.

* Sat Feb 11 2023 Udo Seidel <udoseidel@gmx.de> 6.5.0-1
- Speed up your response time. Now you can react quicker by clicking on any emoji when replying to a story.
- It's now possible to search your message history for individual characters in Chinese and Japanese. 

* Thu Feb 02 2023 Udo Seidel <udoseidel@gmx.de> 6.4.1-1
- Hard at work fixing bugs and making other performance improvements to keep the app running smoothly for you.

* Thu Feb 02 2023 Udo Seidel <udoseidel@gmx.de> 6.4.0-1
- Hard at work fixing bugs and making other performance improvements to keep the app running smoothly for you.

* Fri Jan 27 2023 Udo Seidel <udoseidel@gmx.de> 6.3.0-1
- Double-click on any message row in a chat to start a quoted reply. It's like a shortcut for new thoughts about old ideas. Thanks to @WhyNotHugo and the Signal community for implementing this feature and providing feedback.
- Now it's easier to click outside of an image to dismiss the gallery view without zooming in. Sometimes you just wanted to close, and instead things got too close. Thanks to @jojomatik for the fix!
- Tweaks, bug fixes, and performance enhancements.

* Thu Jan 12 2023 Udo Seidel <udoseidel@gmx.de> 6.2.0-1
- Tweaks, bug fixes, and performance enhancements. Keep on texting, calling, and video chatting as usual
- Removed patch covering not being able to read release date from git

* Thu Dec 15 2022 Udo Seidel <udoseidel@gmx.de> 6.1.0-1
- When you start a group call for small groups (up to 16 people), you can choose to send a ringing notification. Group members will hear a ring if they are on the iOS beta or using Desktop or Android.
- Small tweaks, bug fixes, and performance enhancements.

* Tue Dec 06 2022 Udo Seidel <udoseidel@gmx.de> 6.0.1-1
- Stories are now in Signal! Share disappearing text, images, and video updates with select friends or groups that automatically disappear after 24 hours. For everyone who loves sharing stories, here’s a way to do it privately and without seeing any ads. If you don’t want to see or share stories, you can opt out of it all in your Preferences > Privacy.

* Wed Nov 30 2022 Udo Seidel <udoseidel@gmx.de> 6.0.0-1
- Stories are now in Signal! Share disappearing text, images, and video updates with select friends or groups that automatically disappear after 24 hours. For everyone who loves sharing stories, here’s a way to do it privately and without seeing any ads. If you don’t want to see or share stories, you can opt out of it all in your Preferences > Privacy.

* Thu Nov 10 2022 Udo Seidel <udoseidel@gmx.de> 5.63.1-1
- Hard at work fixing bugs and making other performance improvements to keep the app running smoothly for you.

* Fri Nov 04 2022 Udo Seidel <udoseidel@gmx.de> 5.63.0-1
- Hard at work fixing bugs and making other performance improvements to keep the app running smoothly for you.

* Thu Oct 06 2022 Udo Seidel <udoseidel@gmx.de> 5.62.0-1
- Can’t remember which of your friends named Lou is on your basketball team? Check contact details to see shared groups between you and a friend.
- Easily add a friend to a group from their contact details screen to keep the conversation exciting.

* Fri Sep 30 2022 Udo Seidel <udoseidel@gmx.de> 5.61.1-1
- Fix positioning of submenus in custom titlebar on Windows in RTL mode
- Fix dismissing of forward and other modals

* Thu Sep 29 2022 Udo Seidel <udoseidel@gmx.de> 5.61.0-1
- Facing a conversation with a long list of Voice Notes to listen to? Click play, sit back, and relax - they'll continue playing automatically!
- You can now attach some video flavor to a message along with your vacation photos!

* Wed Sep 21 2022 Udo Seidel <udoseidel@gmx.de> 5.60.0-1
- Small tweaks, bug fixes, and performance enhancements. Thanks for using Signal!

* Thu Sep 15 2022 Udo Seidel <udoseidel@gmx.de> 5.59.0-1
- Small tweaks, bug fixes, and performance enhancements. Thanks for using Signal!

* Thu Sep 08 2022 Udo Seidel <udoseidel@gmx.de> 5.58.0-1
- Tweaks, bug fixes, and performance enhancements. Keep on texting, calling, and video chatting as usual.

* Sat Sep 03 2022 Udo Seidel <udoseidel@gmx.de> 5.57.0-1
- Change the speed of audio messages to either get to the point or catch the details.
- Streamline your emoji searching. Once you’ve pulled up the emoji picker, skip the magnifying glass and just start typing keywords.

* Thu Aug 25 2022 Udo Seidel <udoseidel@gmx.de> 5.56.0-1
- Small tweaks, bug fixes, and performance enhancements. Thanks for using Signal!

* Thu Aug 18 2022 Udo Seidel <udoseidel@gmx.de> 5.55.0-1
- Additional small tweaks, bug fixes, and assorted plans for the future.

* Wed Aug 10 2022 Udo Seidel <udoseidel@gmx.de> 5.54.0-1
- Additional small tweaks, bug fixes, and assorted plans for the future.

* Thu Aug 04 2022 Udo Seidel <udoseidel@gmx.de> 5.53.0-1
- If you’re using the JAWS screen reading program, you can now successfully play voice memos and access longer messages that get shortened behind a “read more” button.
- Additional small tweaks, bug fixes, and performance enhancements. 

* Thu Jul 28 2022 Udo Seidel <udoseidel@gmx.de> 5.52.0-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.

* Tue Jul 26 2022 Udo Seidel <udoseidel@gmx.de> 5.51.1-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.

* Thu Jul 21 2022 Udo Seidel <udoseidel@gmx.de> 5.51.0-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.

* Thu Jul 14 2022 Udo Seidel <udoseidel@gmx.de> 5.50.0-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.

* Mon Jul 11 2022 Udo Seidel <udoseidel@gmx.de> 5.49.0-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.

* Fri Jul 01 2022 Udo Seidel <udoseidel@gmx.de> 5.48.0-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.

* Thu Jun 16 2022 Udo Seidel <udoseidel@gmx.de> 5.46.0-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.

* Thu Jun 02 2022 Udo Seidel <udoseidel@gmx.de> 5.45.0-1
- Dynamic audio indicators in group calls help you see if you're whispering, yelling, or just right.
- Groups you’ve requested to join from your phone (via an invite link) will now show up on Desktop.
- Got a spotty Wi-Fi connection? Not a problem, you can now retry downloading attachments.

* Thu May 26 2022 Udo Seidel <udoseidel@gmx.de> 5.44.1-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.

* Thu May 12 2022 Udo Seidel <udoseidel@gmx.de> 5.43.0-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.

* Fri May 06 2022 Udo Seidel <udoseidel@gmx.de> 5.42.0-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.

* Fri Apr 29 2022 Udo Seidel <udoseidel@gmx.de> 5.41.0-1
- This version contains a number of small tweaks and bug fixes to keep Signal running smoothly.

* Sat Apr 23 2022 Udo Seidel <udoseidel@gmx.de> 5.40.1-1
- Bug fixes including a fix to an issue that would sometimes make it difficult to click on menus.
- Thanks to our open source contributors @dsanders11 and @yusufsahinhamza for contributing to these improvements.

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
