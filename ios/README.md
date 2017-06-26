# MotioSecure on iOS

# Installing

Start by following this  [tutorial](https://www.raywenderlich.com/156966/push-notifications-tutorial-getting-started).

After completing the above tutorial, here's how to send notifications from your codebase. From the tutorial, you should have a public and private key pair for push notifications.

> Doesn't sound familiar? This was downloaded in the last steps of the above tutorial. In your Apple Member Center, visit Certificates, IDs & Profiles -> Identifiers -> App IDs. Select the appropriate App ID, click edit, and scroll down to Push Notifications. Click Create Certification for either production or development. Once downloaded, double-click the files to install in Keychain Access.

Open Keychain Access, navigate to "login," and export the aforementioned certificate as `cert.pem` to `~/Downloads`. Click the dropdown,  export the private key to `key.pem` in `~/Downloads`. In your terminal, start by navigating to `~/Downloads`.

```
cd ~/Downloads
```

Next, convert both to pk12 files. Below, we assume your current certificate file is named `cert.pem`.

```
openssl pkcs12 -in cert.p12 -out cert.pem -clcerts -nokeys
```

This will prompt you for an `Import Password`. Leave it blank, and hit `ENTER`. Next, convert the key.

```
openssl pkcs12 -in key.p12  -out key.pem -nocerts
```

This will prompt you for an `Import Password` again. Leave it blank, and hit `ENTER`. You will then be prompted for a `PEM pass phrase`. Type in a password at least 4 letters long. Note this password won't be used in the final certificate, so any memorizable gibberish is fine. Finally, we encrypt the `pem`.

```
openssl rsa -in key.pem -out keyNoPasswd.pem
```

This will prompt you for your `PEM pass phrase`. Enter that in, and `ENTER` to continue. Finally, merge both into one certificate.

```
cat keyNoPasswd.pem > bundle.pem
cat cert.pem >> bundle.pem
```

In the `apns` package, simply pass the same `bundle.pem` to both `key_file` and `cert_file`. This bundle now contains the private and public keys for your application's push notifications.
