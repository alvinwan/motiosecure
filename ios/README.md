#MotioSecure on iOS

# Installing

To get setup with a sample test, see this [tutorial](https://www.raywenderlich.com/156966/push-notifications-tutorial-getting-started).

Otherwise, here's how to send notifications from your codebase. We start by downloading certificates from the Apple developer site. In your Apple Member Center, visit Certificates, IDs & Profiles -> Identifiers -> App IDs. Select the appropriate App ID, click edit, and scroll down to Push Notifications. Click Create Certification for either production or development. Once downloaded, double-click the files to install in Keychain Access. Open Keychain Access, navigate to "login," and export the certificate as `cert.pem` to `~/Downloads` and the key (click the dropdown arrow by the certificate) to `key.pem` to `~/Downloads`. Next, convert both to pk12 files.

```
openssl pkcs12 -in cert.p12 -out cert.pem -clcerts -nokeys
```

This will prompt you for an `Import Password`. Leave it blank, and hit `ENTER`. Next, convert the key.

```
openssl pkcs12 -in key.p12  -out key.pem -nocerts
```

This will prompt you for an `Import Password` again. Leave it blank, and hit `ENTER`. You will then be prompted for a `PEM pass phrase`. Type in a password at least 4 letters long. Note this password won't be used, so any gibberish is fine. Finally, we encrypt the `pem`.

```
openssl rsa -in key.pem -out keyNoPasswd.pem
```

This will prompt you for your `PEM pass phrase`. Enter that in, and `ENTER` to continue. Finally, merge both into one certificate.

```
cat keyNoPasswd.pem > mergedPushCertificate.pem
cat cert.pem >> mergedPushCertificate.pem
```

In the `apns` package, simply pass the same `mergedPushedCertificate` to both `key_file` and `cert_file`.
