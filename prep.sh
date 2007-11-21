#!/bin/bash
#
# Builds the BootCD reference image, the first of two
# initramfs cpio archives that are concatenated together by
# isolinux/syslinux to form a custom BootCD.
#
# Aaron Klingaman <alk@absarokasoft.com>
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2004-2006 The Trustees of Princeton University
#
# $Id$
#

PATH=/sbin:/bin:/usr/sbin:/usr/bin

# In both a normal CVS environment and a PlanetLab RPM
# build environment, all of our dependencies are checked out into
# directories at the same level as us.
if [ -d ../build ] ; then
    PATH=$PATH:../build
    srcdir=..
else
    echo "Error: Could not find sources in either . or .."
    exit 1
fi

export PATH

. build.common

# pldistro expected as $1 - defaults to planetlab
pldistro=planetlab
[ -n "$@" ] && pldistro=$1

# Packages to install : see <pldistro>-bootcd.lst

# Unnecessary junk
junk=(
lib/obsolete
lib/tls
usr/share/cracklib
usr/share/emacs
usr/share/gnupg
usr/share/i18n
usr/share/locale
usr/share/terminfo
usr/share/zoneinfo
usr/sbin/build-locale-archive
usr/sbin/dbconverter-2
usr/sbin/sasl*
usr/sbin/tcpslice
usr/lib/perl*
usr/lib/locale
usr/lib/sasl*
usr/lib/gconv
usr/lib/tls
)

precious=(
usr/share/i18n/locales/en_US
usr/share/i18n/charmaps/UTF-8.gz
usr/share/locale/en
usr/share/terminfo/l/linux
usr/share/terminfo/v/vt100
usr/share/terminfo/x/xterm
usr/share/zoneinfo/UTC
usr/lib/locale/en_US.utf8
)

# Do not tolerate errors
set -e

# Root of the initramfs reference image
bootcd=$PWD/build/bootcd
install -d -m 755 $bootcd

# Write version number
rpmquery --specfile bootcd.spec --queryformat '%{VERSION}\n' | head -1 >build/version.txt

# Install base system
lst=${pldistro}-bootcd.lst
options=$(pl_getPackagesOptions2 ${pl_DISTRO_NAME} $lst)

pl_setup_chroot $bootcd $options -k

pushd $bootcd

echo "* Removing unnecessary junk"

# Save precious files
tar --ignore-failed-read -cpf precious.tar ${precious[*]}

# Remove unnecessary junk
rm -rf ${junk[*]}

# Restore precious files
tar -xpf precious.tar
rm -f precious.tar

popd

# Install ipnmac (for SuperMicro machines with IPMI)
echo "* Installing IPMI utilities"
install -D -m 755 ipnmac/ipnmac.x86 $bootcd/usr/sbin/ipnmac

# Install configuration files
echo "* Installing configuration files"
for file in fstab mtab modprobe.conf inittab hosts sysctl.conf ; do
    install -D -m 644 conf_files/$file $bootcd/etc/$file
done

# Install initscripts
echo "* Installing initscripts"
for file in pl_sysinit pl_hwinit pl_netinit pl_validateconf pl_boot ; do
    install -D -m 755 conf_files/$file $bootcd/etc/init.d/$file
done

# Install fallback node configuration file
echo "* Installing fallback node configuration file"
install -D -m 644 conf_files/default-net.cnf $bootcd/usr/boot/default-net.cnf

# Copy /etc/passwd out
install -D -m 644 $bootcd/etc/passwd build/passwd

# Root of the isofs
isofs=$PWD/build/isofs
install -d -m 755 $isofs

# Copy the kernel out
for kernel in $bootcd/boot/vmlinuz-* ; do
    if [ -f $kernel ] ; then
	install -D -m 644 $kernel $isofs/kernel
    fi
done

# Don't need /boot anymore
rm -rf $bootcd/boot

# initramfs requires that /init be present
ln -sf /sbin/init $bootcd/init

# Pack the rest into a compressed archive
echo "* Compressing reference image"
(cd $bootcd && find . | cpio --quiet -c -o) | gzip -9 >$isofs/bootcd.img

# Build syslinux
echo "* Building syslinux"
CFLAGS="-Werror -Wno-unused -finline-limit=2000" make -C syslinux

# Install isolinux
echo "* Installing isolinux"
install -D -m 644 syslinux/isolinux.bin $isofs/isolinux.bin

exit 0
