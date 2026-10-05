#!/system/bin/sh
set -eu
stage=/data/local/tmp/g6-eng-stage
backup=/data/local/tmp/g6-stock-20p-backup
lafpart=/dev/block/bootdevice/by-name/laf
abootpart=/dev/block/bootdevice/by-name/aboot
laf_started=0
aboot_started=0
image_sha256() { sha256sum "$1" | cut -d ' ' -f 1; }
cleanup() {
    rc=$?
    trap - EXIT HUP INT TERM
    set +e
    if [ "$rc" -ne 0 ]; then
        echo "ENG_APPLY_FAILED $rc; restoring any partition whose write was attempted"
        if [ "$aboot_started" = 1 ]; then
            dd if="$backup/aboot.img" of="$abootpart" bs=1048576
            sync
            echo "RESTORED_ABOOT_HASH $(image_sha256 "$abootpart")"
        fi
        if [ "$laf_started" = 1 ]; then
            dd if="$backup/laf.img" of="$lafpart" bs=1048576
            sync
            echo "RESTORED_LAF_HASH $(image_sha256 "$lafpart")"
        fi
    fi
    setenforce 1
    getenforce
    exit "$rc"
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
[ "$(id -u)" = 0 ] || exit 10
[ "$(getprop ro.product.device)" = lucye ] || exit 11
[ "$(getprop ro.lge.swversion)" = G600KR20p ] || exit 12
[ "$(blockdev --getsize64 "$lafpart")" = 50331648 ] || exit 13
[ "$(blockdev --getsize64 "$abootpart")" = 2097152 ] || exit 14
[ "$(blockdev --getro "$lafpart")" = 0 ] || exit 15
[ "$(blockdev --getro "$abootpart")" = 0 ] || exit 16
old_aboot=c02d134c868a39c7aa0e9599f513c515023b9ecc25da3ca43d1e3ed2719e77c4
old_laf=24de51b9e6c5b6ec3bd68d7f5fd298677ec1d5ed5aeed35bdd90807ac71c9231
new_aboot=bac7b2809e60cfcb695f0b4afcdfff016b395d546cbd29f36be38696410242f9
new_laf=43e43e6e88223237a0be1e13e50c12c504336e0f6ddac61248d2aac03f78afcd
[ "$(image_sha256 "$backup/aboot.img")" = "$old_aboot" ] || exit 17
[ "$(image_sha256 "$backup/laf.img")" = "$old_laf" ] || exit 18
[ "$(image_sha256 "$abootpart")" = "$old_aboot" ] || exit 19
[ "$(image_sha256 "$lafpart")" = "$old_laf" ] || exit 20
[ "$(stat -c %s "$stage/aboot.img")" = 2097152 ] || exit 21
[ "$(stat -c %s "$stage/laf.img")" = 50331648 ] || exit 22
[ "$(image_sha256 "$stage/aboot.img")" = "$new_aboot" ] || exit 23
[ "$(image_sha256 "$stage/laf.img")" = "$new_laf" ] || exit 24
echo ALL_PREFLIGHT_CHECKS_PASSED
laf_started=1
dd if="$stage/laf.img" of="$lafpart" bs=1048576
sync
[ "$(image_sha256 "$lafpart")" = "$new_laf" ] || exit 25
echo LAF_WRITE_READBACK_VERIFIED
aboot_started=1
dd if="$stage/aboot.img" of="$abootpart" bs=1048576
sync
[ "$(image_sha256 "$abootpart")" = "$new_aboot" ] || exit 26
echo ABOOT_WRITE_READBACK_VERIFIED
echo ENG_APPLY_COMPLETE_NO_REBOOT
