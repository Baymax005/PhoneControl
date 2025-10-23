
#!/bin/bash
# APK Builder Script
# 
# To actually build this, you need:
# 1. Android Studio
# 2. Java JDK
# 3. APKTool or similar
#
# Build command:
# apktool b -o ChipsPanda.apk ./source
# jarsigner -keystore my-key.keystore ChipsPanda.apk alias_name
# zipalign -v 4 ChipsPanda.apk ChipsPanda_signed.apk
