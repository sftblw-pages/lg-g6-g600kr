#!/sbin/sh
# Read-only verification derived from the tested G600KR procedure.
# Arguments: recovery serial, verified pre-install full boot SHA-256, optional --before.
set -eu
test "$(id -u)" = 0
test "$(getprop ro.twrp.version)" = 3.5.2_10-0
test "${1-}" != ''
test "$(getprop ro.serialno)" = "$1"
expected_boot=${2-}
test "${#expected_boot}" = 64
case "$expected_boot" in *[!0-9a-f]*) exit 64 ;; esac
test "$(getprop ro.product.device)" = h870
test "$(getprop ro.bionic.arch)" = arm64
test -z "$(getprop ro.boot.slot_suffix)"
test "$(cat /sys/class/power_supply/battery/capacity)" -ge 50
boot=/dev/block/bootdevice/by-name/boot
system=/dev/block/bootdevice/by-name/system
test "$(blockdev --getsize64 "$boot")" = 41943040
test "$(blockdev --getsize64 "$system")" = 5863636992
test "$(sha256sum "$boot" | awk '{print $1}')" = "$expected_boot"
get_block_for_mount_point() {
  grep -v '^#' /etc/recovery.fstab | grep "[[:blank:]]$1[[:blank:]]" | tail -n1 | tr -s '[:blank:]' ' ' | cut -d' ' -f1
}
fstab_entry=$(get_block_for_mount_point /system)
[ -n "$fstab_entry" ] || fstab_entry=$(get_block_for_mount_point /)
[ -n "$fstab_entry" ] || fstab_entry=$(get_block_for_mount_point /system_root)
resolved=${fstab_entry:-$system}
test -b "$resolved"
test "$(readlink -f "$resolved")" = "$(readlink -f "$system")"
mp=/tmp/gapps-verify
mkdir -p "$mp"
mount -t ext4 -o ro "$system" "$mp"
trap 'cd /; umount "$mp"' EXIT
grep -Fqx 'ro.build.version.sdk=34' "$mp/system/build.prop"
grep -Fqx 'ro.lineage.version=21.0-20260531-UNOFFICIAL-h870' "$mp/system/build.prop"
cd "$mp/system/vendor"
echo '96e909eb2080ae518b52c34a1a195baa94f0b9478a685a2b53adbccfd11b47af  firmware/fw_bcmdhd.bin' | sha256sum -c -
echo '96e909eb2080ae518b52c34a1a195baa94f0b9478a685a2b53adbccfd11b47af  firmware/fw_bcmdhd_apsta.bin' | sha256sum -c -
echo 'f8879b2d35cca360746b34c6e60c3a4e145d6d465d18d58951ec1a8af48f00b6  firmware/fw_bcmdhd_mfg.bin' | sha256sum -c -
echo 'ccc13dfab7cf7c1025ba13b6cedc38255e210218619bef91d5083c505e2e7bde  etc/wifi/bcmdhd.cal' | sha256sum -c -
echo '831a21ba21842cccd681d0b79045441c8902b36adbb65f93bbcf5fd8940a69d4  etc/wifi/4359_lg.clm_blob' | sha256sum -c -
df -k "$mp" /tmp
grep -E 'MemTotal|MemAvailable|MemFree|Shmem' /proc/meminfo
if [ "${3-}" != --before ]; then
    cd "$mp"
    sha256sum -c /tmp/gapps-installed-files.sha256
    test -s system/addon.d/30-gapps.sh
    awk '{print $2}' /tmp/gapps-installed-files.sha256 | while IFS= read -r file; do
        test "$(stat -c '%u:%g:%a' "$file")" = 0:0:644
        ls -lZ "$file" | grep -q 'u:object_r:system_file:s0'
    done
    test "$(stat -c '%u:%g:%a' system/addon.d/30-gapps.sh)" = 0:0:755
    ls -ldZ system/product/priv-app/Phonesky system/product/priv-app/GmsCore system/system_ext/priv-app/GoogleServicesFramework
    echo GAPPS_FILE_PERMISSIONS_VERIFIED
    echo GAPPS_FILES_BOOT_AND_WIFI_VERIFIED
else
    echo GAPPS_DEVICE_PREFLIGHT_PASSED
fi
cd /
