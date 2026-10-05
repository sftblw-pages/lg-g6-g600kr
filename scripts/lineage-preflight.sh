#!/sbin/sh
set -eu
image_sha256() { sha256sum "$1" | cut -d ' ' -f 1; }
[ "$(id -u)" = 0 ]
[ "$(getprop ro.twrp.version)" = 3.5.2_10-0 ]
[ "$(getprop ro.product.device)" = h870 ]
[ "$(blockdev --getsize64 /dev/block/bootdevice/by-name/system)" = 5863636992 ]
[ "$(blockdev --getsize64 /dev/block/bootdevice/by-name/boot)" = 41943040 ]
[ "$(blockdev --getsize64 /dev/block/bootdevice/by-name/userdata)" = 24956108800 ]
[ "$(cat /sys/class/power_supply/battery/capacity)" -ge 50 ]
[ "$(stat -c %s /tmp/g6-lineage21.zip)" = 968057157 ]
[ "$(image_sha256 /tmp/g6-lineage21.zip)" = 7ecb0c0d4a47fc9b748177eaccf93db2f423cdbe28838ed68041041627c9a774 ]
[ "$(image_sha256 /dev/block/bootdevice/by-name/aboot)" = bac7b2809e60cfcb695f0b4afcdfff016b395d546cbd29f36be38696410242f9 ]
recovery_sha=$(dd if=/dev/block/bootdevice/by-name/recovery bs=4096 count=8510 2>/dev/null | sha256sum | cut -d ' ' -f 1)
[ "$recovery_sha" = e0c4134402fcd1697cc7395eb22a0ee2742837c933995898340e75cafabd6667 ]
echo LINEAGE_INSTALL_PREFLIGHT_PASSED
