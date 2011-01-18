#
# $Id$
#
%define url $URL$

%define nodefamily %{pldistro}-%{_arch}

%define name bootcd-%{nodefamily}
%define version 4.2
%define taglevel 19

# pldistro already in the rpm name
#%define release %{taglevel}%{?pldistro:.%{pldistro}}%{?date:.%{date}}
%define release %{taglevel}%{?date:.%{date}}

Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab %{plrelease}
URL: %(echo %{url} | cut -d ' ' -f 2)

Summary: Boot CD material for %{nodefamily}
Name: %{name}
Version: %{version}
Release: %{release}
License: BSD
Group: System Environment/Base
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
# other archs must be able to install this
BuildArch: noarch

Requires: dosfstools, mkisofs, gzip, mtools, syslinux

Requires: pyplnet

AutoReqProv: no
%define debug_package %{nil}

%description
The Boot CD securely boots PlanetLab nodes into an immutable
environment.

%prep
%setup -q

%build
[ -d BootCD ] || ln -s bootcd BootCD
pushd BootCD

# Build the reference image
./prep.sh %{pldistro} %{nodefamily}

popd

%install
rm -rf $RPM_BUILD_ROOT

pushd  BootCD

# Install the reference image and build scripts
install -d -m 755 $RPM_BUILD_ROOT/%{_datadir}/%{name}
install -m 755 build.sh $RPM_BUILD_ROOT/%{_datadir}/%{name}/
install -m 755 kvariant.sh $RPM_BUILD_ROOT/%{_datadir}/%{name}/
tar cpf - \
    build/isofs/bootcd.img \
    build/isofs/kernel \
    build/passwd \
    build/version.txt \
    build/nodefamily \
    configurations | \
    tar -C $RPM_BUILD_ROOT/%{_datadir}/%{name}/ -xpf -

popd
    
%clean
rm -rf $RPM_BUILD_ROOT

# If run under sudo
if [ -n "$SUDO_USER" ] ; then
    # Allow user to delete the build directory
    chown -h -R $SUDO_USER .
    # Some temporary cdroot files like /var/empty/sshd and
    # /usr/bin/sudo get created with non-readable permissions.
    find . -not -perm +0600 -exec chmod u+rw {} \;
    # Allow user to delete the built RPM(s)
    chown -h -R $SUDO_USER %{_rpmdir}/*
fi

%files
%defattr(-,root,root,-)
%{_datadir}/%{name}

%post
[ -f /etc/planetlab/nodefamily ] || { mkdir -p /etc/planetlab ; echo %{nodefamily} > /etc/planetlab/nodefamily ; }

%changelog
* Tue Jan 18 2011 S.Çağlar Onur <caglar@cs.princeton.edu> - bootcd-4.2-19
- Introduce a quick hack for 2.6.32 based BootCD

* Thu Jan 06 2011 S.Çağlar Onur <caglar@cs.princeton.edu> - bootcd-4.2-18
- handle directory name changes

* Sat Jan 09 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootCD-4.2-17
- support for fedora 12

* Sun Dec 27 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootCD-4.2-16
- fix build on fedora12

* Fri Sep 04 2009 Stephen Soltesz <soltesz@cs.princeton.edu> - BootCD-4.2-15
- record the ntp time to the hwclock.  this is a bootcd operation, but it is
- repeated in the bootmanager to handle all CDs without this operation

* Mon Jun 29 2009 Marc Fiuczynski <mef@cs.princeton.edu> - BootCD-4.2-14
- Daniel's update to generalize the kvariant support.

* Wed Apr 08 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootCD-4.2-13
- robust to node config file specified with a relative path

* Tue Apr 07 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootCD-4.2-12
- fix specfile - 4.2-11 would not build

* Tue Apr 07 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootCD-4.2-11
- Added support for handling kernel variants
- http://svn.planet-lab.org/wiki/BootcdVariant

* Tue Mar 24 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootCD-4.2-10
- mkfs.vfat output removed prior to invokation - fix needed on fedora 10

* Tue Dec 30 2008 Marc Fiuczynski <mef@cs.princeton.edu> - BootCD-4.2-9
- Added kupdate.sh

* Sat Dec 13 2008 Daniel Hokka Zakrisson <daniel@hozac.com> - BootCD-4.2-8
- Use pyplnet.
- Add a site_admin account to the BootCD.
- Add some explanations for common errors.

* Tue Dec 02 2008 Daniel Hokka Zakrisson <daniel@hozac.com> - BootCD-4.2-7
- Allow multiple -k options to the build.sh script.
- Probe devices in PCI bus order.

* Fri Nov 14 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootCD-4.2-6
- add support for fedora9 images - compliant with upstart
- formerly monolythic dir 'conf_files/' split into 'etc/' and 'initscripts/'

* Tue Sep 23 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootCD-4.2-5
- cosmetic - pl_boot to display timestamps

* Mon Aug 04 2008 Stephen Soltesz <soltesz@cs.princeton.edu> - BootCD-4.2-4
- adds -k as an argument to build.sh to pass additional kernel parameters to the
- bootcd and kexec kernel.

* Mon May 05 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootCD-4.2-3
- rpm release tag does not need pldistro as it is already part of the rpm name

* Thu Apr 24 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootCD-4.2-2
- change location of nodefamily in /etc/planetlab/

* Wed Apr 23 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootCD-4.2-1
- new name for the rpm, to allow simultaneous rpm-installs for several nodefamily (pldistro+arch)
- now installs in /usr/share/bootcd-<nodefamily> with a legacy symlink (requires MyPLC-4.2-7) 
- nodefamily exported under bootcd.img in /etc/nodefamily (for bm) and under build/nodefamily (for build.sh)

* Wed Mar 26 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootCD-3.4-4 BootCD-3.4-5
- kargs.txt for serial boot fixed: now properly exposed to bootmanager through the overlay image
- build.sh cleaned up in the process
- actual location of selected node config file displayed
- import pypci rather than pypciscan

* Thu Feb 14 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - bootcd-3.4-3 bootcd-3.4-4
- build.sh support for -s <console_spec> (recommended vs using type)
- build.sh cleanup - usage clearer wrt types - removed old code
- fixed modprobe with args in pl_hwinit

* Thu Jan 31 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - bootcd-3.4-2 bootcd-3.4-3
- load floppy with modprobe flags
- support for creating a usb partition
- removed obsolete files newbuild.sh, bootcustom.sh and cdcustom.sh

* Mon Jan 29 2006 Marc E. Fiuczynski <mef@cs.princeton.edu> - 
- added biginitrd usb image

* Fri Sep  2 2005 Mark Huang <mlhuang@cotton.CS.Princeton.EDU> - 
- Initial build.

%define module_current_branch 3.4
