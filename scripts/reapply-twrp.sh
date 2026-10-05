#!/system/bin/sh
set -eu
part=/dev/block/bootdevice/by-name/recovery
img=/data/local/tmp/twrp-3.5.2_10-0-h870.img
backup=/data/local/tmp/g6-stock-20p-backup/recovery.img
expected=e0c4134402fcd1697cc7395eb22a0ee2742837c933995898340e75cafabd6667
started=0
image_sha256() { sha256sum "$1" | cut -d ' ' -f 1; }
cleanup() {
    rc=$?
    trap - EXIT HUP INT TERM
    set +e
    if [ "$rc" -ne 0 ] && [ "$started" = 1 ]; then
        echo TWRP_WRITE_FAILED_RESTORING_STOCK
        dd if="$backup" of="$part" bs=1048576
        sync
        echo "RESTORED_RECOVERY_HASH $(image_sha256 "$part")"
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
[ "$(getprop ro.lge.swversion)" = G600LR20p ] || exit 12
[ "$(getprop init.svc.flash_recovery)" = stopped ] || exit 13
[ "$(blockdev --getsize64 "$part")" = 42467328 ] || exit 14
[ "$(blockdev --getro "$part")" = 0 ] || exit 15
[ "$(stat -c %s "$img")" = 34856960 ] || exit 16
[ "$(image_sha256 "$img")" = "$expected" ] || exit 17
[ "$(image_sha256 "$backup")" = c4a87ca17d31613c69aab154ccb3a84141ac36dd7ff315cc79a0e842b1c2b9a3 ] || exit 18
current=$(image_sha256 "$part")
case "$current" in
    c4a87ca17d31613c69aab154ccb3a84141ac36dd7ff315cc79a0e842b1c2b9a3|60f9f0a28bc2fc326710c94929ea2b76a445a2a1e82f8876117ac29b701954fe) ;;
    *) echo 'Unexpected recovery image; stop and inspect before writing.'; exit 19 ;;
esac
[ "$(image_sha256 /dev/block/bootdevice/by-name/aboot)" = bac7b2809e60cfcb695f0b4afcdfff016b395d546cbd29f36be38696410242f9 ] || exit 20
echo TWRP_REAPPLY_PREFLIGHT_PASSED
started=1
dd if="$img" of="$part" bs=4096
sync
actual=$(dd if="$part" bs=4096 count=8510 2>/dev/null | sha256sum | cut -d ' ' -f 1)
[ "$actual" = "$expected" ] || exit 21
echo TWRP_REAPPLY_READBACK_VERIFIED
