#!/bin/bash

# Usage: ./packager.sh <team ID>
# Instructions taken from https://github.com/electron-userland/electron-osx-sign/wiki/Packaging-and-Submitting-an-Electron-App-to-the-Mac-App-Store
pyinstaller motiosecure/api.py --distpath dist --hidden-import sklearn.neighbors.typedefs
electron-packager . "MotioSecure" --app-bundle-id=com.alvinwan.mac.MotioSecure --app-version=0.1.2 --build-version=0.1.2 --electron-version=1.6.11 --icon=Icon.icns --overwrite
electron-osx-sign "MotioSecure-mas-x64/MotioSecure.app" --verbose
electron-osx-sign "MotioSecure-mas-x64/MotioSecure.app" {MotioSecure-mas-x64/MotioSecure.app/Contents/Resources/app/dist/api/*.so,MotioSecure-mas-x64/MotioSecure.app/Contents/Resources/app/dist/api/**/*.so} --verbose
electron-osx-sign "MotioSecure-mas-x64/MotioSecure.app" --identity="3rd Party Mac Developer Application: Alvin Wan ($1)" --verbose
electron-osx-flat "MotioSecure-mas-x64/MotioSecure.app" --verbose
electron-osx-flat "MotioSecure-mas-x64/MotioSecure.app" --identity="3rd Party Mac Developer Installer: Alvin Wan ($1)" --verbose
