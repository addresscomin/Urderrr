# GUARD CLEAR

Android installed-app manager prototype.

Features: searchable app list, package names, active device-admin app indicator, App Info shortcut, and uninstall flow using Android's system confirmation UI. System apps are not offered for uninstall.

Device-admin apps: open Android Device Admin Settings and deactivate only apps you own/manage and are authorized to change. It does not bypass Device Owner, MDM, parental-control, or other management restrictions.

## Build
Open the `GuardClear` folder in Android Studio or run Gradle 8.9 with Android SDK 35:

```bash
gradle assembleDebug
```

APK output: `app/build/outputs/apk/debug/app-debug.apk`
