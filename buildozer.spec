[app]

title = SoloForge Local Game

package.name = soloforgegame
package.domain = org.soloforge

source.dir = .
source.include_exts = py,png,jpg,jpeg,atlas

version = 0.1

requirements = python3,pygame

orientation = portrait

fullscreen = 0

android.permissions = INTERNET,ACCESS_WIFI_STATE,CHANGE_WIFI_MULTICAST_STATE

android.api = 35
android.minapi = 24

[buildozer]

log_level = 2
warn_on_root = 1
