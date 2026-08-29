[app]
title = SoloForge Local Game
package.name = soloforgegame
package.domain = org.soloforge
source.include_exts = py,png,jpg,kv,atlas
source.dir = .
version = 0.1
requirements = python3,kivy,pygame
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, ACCESS_WIFI_STATE, CHANGE_WIFI_MULTICAST_STATE

# تحديد إصدارات أندرويد المستقرة لتجنب أخطاء الترجمة
android.api = 31
android.min_api = 21
android.sdk = 31
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
