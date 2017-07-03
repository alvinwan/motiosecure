#!/bin/bash

# Usage: ./packager.sh <team ID>
# Instructions taken from https://github.com/electron-userland/electron-osx-sign/wiki/Packaging-and-Submitting-an-Electron-App-to-the-Mac-App-Store
electron-packager . "MotioSecure" --app-bundle-id=com.alvinwan.mac.MotioSecure --app-version=0.1.1 --build-version=0.1.1 --platform=mas --arch=x64 --electron-version=0.36.7 --icon=Icon.icns --overwrite
electron-osx-sign "MotioSecure-mas-x64/MotioSecure.app" --verbose
electron-osx-sign "MotioSecure-mas-x64/MotioSecure.app" {MotioSecure-mas-x64/MotioSecure.app/Contents/Resources/app/dist/api/*.so,MotioSecure-mas-x64/MotioSecure.app/Contents/Resources/app/dist/api/**/*.so} --verbose
electron-osx-sign "MotioSecure-mas-x64/MotioSecure.app" --identity="3rd Party Mac Developer Application: Alvin Wan ($1)" --verbose
electron-osx-flat "MotioSecure-mas-x64/MotioSecure.app" --verbose
electron-osx-flat "MotioSecure-mas-x64/MotioSecure.app" --identity="3rd Party Mac Developer Installer: Alvin Wan ($1)" --verbose
