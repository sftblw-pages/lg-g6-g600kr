#!/sbin/sh
set -eu
cd /tmp/g6-wifi
# Generated local SHA256SUMS includes this device's private rollback files.
test "$(id -u)" = 0
test "$(getprop ro.twrp.version)" = 3.5.2_10-0
test "$(getprop ro.serialno)" = "$(cat expected-serial.txt)"
boot=/dev/block/bootdevice/by-name/boot
system=/dev/block/bootdevice/by-name/system
test "$(blockdev --getsize64 "$boot")" = 41943040
test "$(blockdev --getsize64 "$system")" = 5863636992
sha256sum -c SHA256SUMS
image_sha256() { sha256sum "$1" | awk '{print $1}'; }
test "$(image_sha256 before/boot-partition.img)" = "$(cat before/boot.sha256)"
test "$(image_sha256 /dev/block/bootdevice/by-name/aboot)" = bac7b2809e60cfcb695f0b4afcdfff016b395d546cbd29f36be38696410242f9
mp=/tmp/g6-wifi-restore
mounted=0
finish() {
    result=$?
    trap - EXIT HUP INT TERM
    sync
    if [ "$mounted" = 1 ]; then umount "$mp" || true; fi
    exit "$result"
}
trap finish EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir -p "$mp"
mount -t ext4 -o ro "$system" "$mp"
mounted=1
vendor="$mp/system/vendor"
test -f "$vendor/etc/wifi/bcmdhd.cal"
grep -Fqx 'ro.lineage.version=21.0-20260531-UNOFFICIAL-h870' "$mp/system/build.prop"
mount -o remount,rw "$mp"
for name in fw_bcmdhd.bin fw_bcmdhd_apsta.bin fw_bcmdhd_mfg.bin; do
    cat "before/$name" > "$vendor/firmware/$name"
    test "$(image_sha256 "$vendor/firmware/$name")" = "$(image_sha256 "before/$name")"
done
cat before/bcmdhd.cal > "$vendor/etc/wifi/bcmdhd.cal"
test "$(image_sha256 "$vendor/etc/wifi/bcmdhd.cal")" = "$(image_sha256 before/bcmdhd.cal)"
rm -f "$vendor/etc/wifi/4359_lg.clm_blob"
dd if=before/boot-partition.img of="$boot" bs=4096
sync
test "$(image_sha256 "$boot")" = "$(cat before/boot.sha256)"
umount "$mp"
mounted=0
echo KNOWN_BOOTABLE_LINEAGE_RESTORED_AND_VERIFIED_NO_REBOOT
