#!/system/bin/sh
set -eu
trap 'setenforce 1' EXIT HUP INT TERM
[ "$(id -u)" = 0 ] || exit 10
[ "$(getprop ro.product.device)" = lucye ] || exit 11
[ "$(getprop ro.lge.swversion)" = G600KR20p ] || exit 12
out=/data/local/tmp/g6-stock-20p-backup
[ ! -e "$out" ] || exit 13
umask 077
mkdir "$out"
names='aboot abootbak laf lafbak boot recovery recoverybak devinfo xbl xblbak xbl2 xbl2bak raw_resources raw_resourcesbak modemst1 modemst2 fsg fsc persist persistent factory misc drm eksst encrypt keystore sec cdt tz tzbak rpm rpmbak hyp hypbak pmic pmicbak devcfg devcfgbak keymaster keymasterbak cmnlib cmnlibbak cmnlib64 cmnlib64bak modem rct sns ssd apdp msadp dpo'
for name in $names; do
    src=/dev/block/bootdevice/by-name/$name
    [ -b "$src" ] || exit 14
    size=$(blockdev --getsize64 "$src")
    [ "$size" -gt 0 ] && [ "$size" -le 134217728 ] || exit 15
    printf '%s %s\n' "$name" "$size" >> "$out/sizes.txt"
    dd if="$src" of="$out/$name.img" bs=1048576
    [ "$(stat -c %s "$out/$name.img")" = "$size" ] || exit 16
    sha256sum "$out/$name.img" >> "$out/SHA256SUMS.txt"
    chown 2000:2000 "$out/$name.img"
    printf 'BACKED_UP %s %s\n' "$name" "$size"
done
for disk in sda sdb sdc sdd sde sdf sdg; do
    dd if=/dev/block/$disk of="$out/$disk-gpt-primary.bin" bs=4096 count=6
    sha256sum "$out/$disk-gpt-primary.bin" >> "$out/SHA256SUMS.txt"
    chown 2000:2000 "$out/$disk-gpt-primary.bin"
done
chown 2000:2000 "$out" "$out/sizes.txt" "$out/SHA256SUMS.txt"
printf 'BACKUP_COMPLETE\n'
