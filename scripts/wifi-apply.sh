#!/sbin/sh
set -eu
case "${1-}" in ''|--check-only) ;; *) exit 64 ;; esac
cd /tmp/g6-wifi
# Generated local SHA256SUMS includes this device's private rollback files.
test "$(id -u)" = 0
test "$(getprop ro.twrp.version)" = 3.5.2_10-0
test "$(getprop ro.product.device)" = h870
test "$(getprop ro.serialno)" = "$(cat expected-serial.txt)"
boot=/dev/block/bootdevice/by-name/boot
system=/dev/block/bootdevice/by-name/system
test "$(blockdev --getsize64 "$boot")" = 41943040
test "$(blockdev --getsize64 "$system")" = 5863636992
test "$(cat /sys/class/power_supply/battery/capacity)" -ge 50
sha256sum -c SHA256SUMS
image_sha256() { sha256sum "$1" | awk '{print $1}'; }
test "$(image_sha256 "$boot")" = "$(cat before/boot.sha256)"
test "$(image_sha256 /dev/block/bootdevice/by-name/aboot)" = bac7b2809e60cfcb695f0b4afcdfff016b395d546cbd29f36be38696410242f9
test "$(dd if=/dev/block/bootdevice/by-name/recovery bs=4096 count=8510 2>/dev/null | sha256sum | awk '{print $1}')" = e0c4134402fcd1697cc7395eb22a0ee2742837c933995898340e75cafabd6667
mp=/tmp/g6-wifi-system
vendor="$mp/system/vendor"
phase=preflight
mounted=0
restore_originals() {
    set +e
    echo RESTORING_KNOWN_BOOTABLE_LINEAGE
    mount -o remount,rw "$mp"
    for name in fw_bcmdhd.bin fw_bcmdhd_apsta.bin fw_bcmdhd_mfg.bin; do
        cat "before/$name" > "$vendor/firmware/$name"
    done
    cat before/bcmdhd.cal > "$vendor/etc/wifi/bcmdhd.cal"
    rm -f "$vendor/etc/wifi/4359_lg.clm_blob"
    dd if=before/boot-partition.img of="$boot" bs=4096
    sync
    image_sha256 "$boot"
    echo "EXPECTED_RESTORED_BOOT_$(cat before/boot.sha256)"
}
finish() {
    result=$?
    trap - EXIT HUP INT TERM
    if [ "$result" -ne 0 ] && [ "$phase" = writing ]; then restore_originals; fi
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
test -f "$vendor/etc/wifi/bcmdhd.cal"
test -f "$mp/system/build.prop"
grep -Fqx 'ro.lineage.version=21.0-20260531-UNOFFICIAL-h870' "$mp/system/build.prop"
for name in fw_bcmdhd.bin fw_bcmdhd_apsta.bin fw_bcmdhd_mfg.bin; do
    test "$(image_sha256 "$vendor/firmware/$name")" = "$(image_sha256 "before/$name")"
done
test "$(image_sha256 "$vendor/etc/wifi/bcmdhd.cal")" = "$(image_sha256 before/bcmdhd.cal)"
test ! -e "$vendor/etc/wifi/4359_lg.clm_blob"
echo WIFI_FIX_PREFLIGHT_PASSED
if [ "${1-}" = --check-only ]; then
    echo READ_ONLY_PREFLIGHT_COMPLETE
    exit 0
fi
mount -o remount,rw "$mp"
phase=writing
for name in fw_bcmdhd.bin fw_bcmdhd_apsta.bin fw_bcmdhd_mfg.bin; do
    cat "stock/$name" > "$vendor/firmware/$name"
    chmod 0644 "$vendor/firmware/$name"
    chown 0:0 "$vendor/firmware/$name"
    test "$(image_sha256 "$vendor/firmware/$name")" = "$(image_sha256 "stock/$name")"
done
cat stock/bcmdhd.cal > "$vendor/etc/wifi/bcmdhd.cal"
cat stock/4359_lg.clm_blob > "$vendor/etc/wifi/4359_lg.clm_blob"
chmod 0644 "$vendor/etc/wifi/bcmdhd.cal" "$vendor/etc/wifi/4359_lg.clm_blob"
chown 0:0 "$vendor/etc/wifi/bcmdhd.cal" "$vendor/etc/wifi/4359_lg.clm_blob"
chcon u:object_r:vendor_configs_file:s0 "$vendor/etc/wifi/4359_lg.clm_blob"
for name in bcmdhd.cal 4359_lg.clm_blob; do
    test "$(image_sha256 "$vendor/etc/wifi/$name")" = "$(image_sha256 "stock/$name")"
done
sync
echo STOCK_G600_WIFI_FILES_READBACK_VERIFIED
dd if=boot-g600kr-wifi.img of="$boot" bs=4096
sync
test "$(dd if="$boot" bs=4096 count=4310 2>/dev/null | sha256sum | awk '{print $1}')" = cbf044c07b499c4a3f94e587131e92d3c61b83946f2b6809e4477cd32f859eb5
phase=complete
echo WIFI_KERNEL_READBACK_VERIFIED_NO_REBOOT
