#!/bin/bash

export PLATFORM=darwin
export ELECTRON_VERSION=1.6.11

# Usage: ./packager.sh <team ID>
# Instructions taken from https://github.com/electron-userland/electron-osx-sign/wiki/Packaging-and-Submitting-an-Electron-App-to-the-Mac-App-Store
pyinstaller motiosecure/api.py --distpath dist --hidden-import sklearn.neighbors.typedefs
electron-packager . "MotioSecure" --app-bundle-id=com.alvinwan.mac.MotioSecure --platform=$PLATFORM --app-version=0.1.2 --build-version=0.1.2 --electron-version=$ELECTRON_VERSION --icon=Icon.icns --overwrite
electron-osx-sign "MotioSecure-$PLATFORM-x64/MotioSecure.app" --verbose
electron-osx-sign "MotioSecure-$PLATFORM-x64/MotioSecure.app" {MotioSecure-$PLATFORM-x64/MotioSecure.app/Contents/Resources/app/dist/api/*.so,MotioSecure-$PLATFORM-x64/MotioSecure.app/Contents/Resources/app/dist/api/**/*.so} --verbose
electron-osx-sign "MotioSecure-$PLATFORM-x64/MotioSecure.app" --identity="3rd Party Mac Developer Application: Alvin Wan ($1)" --verbose --no-gatekeeper-assess
electron-osx-flat "MotioSecure-$PLATFORM-x64/MotioSecure.app" --verbose
electron-osx-flat "MotioSecure-$PLATFORM-x64/MotioSecure.app" --identity="3rd Party Mac Developer Installer: Alvin Wan ($1)" --verbose --no-gatekeeper-assess
