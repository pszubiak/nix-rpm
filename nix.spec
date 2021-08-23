%global git_sha 2cd1a5b8f31627a09ac34afcbb0f76e90606204f

Name:           nix
Version:        2.4.0~1.g2cd1a5b8
Release:        2%{?dist}
Summary:        Nix is a purely functional package manager

License:        LGPLv2+
URL:            https://nixos.org/nix
Source0:        https://github.com/NixOS/nix/archive/%{git_sha}.tar.gz

BuildRequires:  autoconf
BuildRequires:  autoconf-archive
BuildRequires:  automake
BuildRequires:  bison
BuildRequires:  chrpath
BuildRequires:  boost-devel
BuildRequires:  brotli-devel
BuildRequires:  bzip2-devel
BuildRequires:  editline-devel
BuildRequires:  flex
BuildRequires:  gc-devel
%if 0%{?fedora} || 0%{?eln}
BuildRequires:  gcc-c++
%endif
%if 0%{?el8}
BuildRequires:  gcc-toolset-9-gcc-c++
%endif
BuildRequires:  gtest-devel
BuildRequires:  jq
BuildRequires:  libarchive-devel
BuildRequires:  libcpuid-devel
BuildRequires:  libcurl-devel
BuildRequires:  libseccomp-devel
BuildRequires:  libsodium-devel
BuildRequires:  lowdown-devel
BuildRequires:  openssl-devel
BuildRequires:  sqlite-devel
BuildRequires:  xz-devel

Requires:       busybox


%description
Nix is a powerful package manager for Linux and other Unix systems
that makes package management reliable and reproducible.
Please refer to the Nix manual for more details.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description   devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -q -n %{name}-%{git_sha}


%build
%if 0%{?el8}
# Enalbe GCC 9 for RHEL
export PATH=/opt/rh/gcc-toolset-9/root/usr/bin${PATH:+:${PATH}}
export MANPATH=/opt/rh/gcc-toolset-9/root/usr/share/man:${MANPATH}
export INFOPATH=/opt/rh/gcc-toolset-9/root/usr/share/info${INFOPATH:+:${INFOPATH}}
export PCP_DIR=/opt/rh/gcc-toolset-9/root
export LD_LIBRARY_PATH=/opt/rh/gcc-toolset-9/root/usr/lib64:${LD_LIBRARY_PATH}
export PKG_CONFIG_PATH=/opt/rh/gcc-toolset-9/root/usr/lib64/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}

# Compensate lack of gtest .pc file for RHEL
export GTEST_CFLAGS=" -I/usr/include/gtest"
export GTEST_LIBS=" -lgtest -lgtest_main"
%endif

%undefine _hardened_build

./bootstrap.sh
%configure --disable-doc-gen --localstatedir=/nix/var --with-sandbox-shell=/sbin/busybox
make %{?_smp_mflags}


%install
%if 0%{?el8}
# Enalbe GCC 9 for RHEL
export PATH=/opt/rh/gcc-toolset-9/root/usr/bin${PATH:+:${PATH}}
export MANPATH=/opt/rh/gcc-toolset-9/root/usr/share/man:${MANPATH}
export INFOPATH=/opt/rh/gcc-toolset-9/root/usr/share/info${INFOPATH:+:${INFOPATH}}
export PCP_DIR=/opt/rh/gcc-toolset-9/root
export LD_LIBRARY_PATH=/opt/rh/gcc-toolset-9/root/usr/lib64:${LD_LIBRARY_PATH}
export PKG_CONFIG_PATH=/opt/rh/gcc-toolset-9/root/usr/lib64/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}
%endif

make DESTDIR=%{buildroot} install

# Create Nix store
mkdir -p %{buildroot}/nix/store

# Remove init scripts
rm -r %{buildroot}%{_sysconfdir}/init

# fix permission of nix profile
# (until this is fixed in the relevant Makefile)
chmod -x %{buildroot}%{_sysconfdir}/profile.d/nix.sh

# make per-user directories
for d in profiles gcroots;
do
  mkdir -p %{buildroot}/nix/var/nix/$d/per-user
  chmod 1777 %{buildroot}/nix/var/nix/$d/per-user
done
for i in db temproots ; do
  mkdir %{buildroot}/nix/var/nix/$i
done

# Remove RPATHs for check-rpaths
chrpath -d %{buildroot}/usr/bin/nix
chrpath -d %{buildroot}/usr/lib64/*.so

%check
make check


%pre
# Setup build group
if ! getent group "nixbld" >/dev/null; then
  groupadd -r "nixbld"
fi

# Setup build users
for i in $(seq 32); do
  if ! getent passwd "nixbld$i" >/dev/null; then
    useradd -r -g "nixbld" -G "nixbld" -d /var/empty \
      -s /sbin/nologin \
      -c "Nix build user $i" "nixbld$i"
  fi
done


%files
%{_bindir}/nix*
%{_libdir}/*.so
%{_libexecdir}/nix
%{_prefix}/lib/systemd/system/*
%config(noreplace) %{_sysconfdir}/*
%{_datadir}/*
%dir /nix
%attr(1775,root,nixbld) /nix/store
%dir /nix/var
%dir %attr(775,root,nixbld) /nix/var/nix
%ghost /nix/var/nix/daemon-socket/socket
%attr(775,root,nixbld) /nix/var/nix/temproots
%attr(775,root,nixbld) /nix/var/nix/db

%files devel
%{_includedir}/nix
%{_libdir}/pkgconfig/*.pc


%changelog
* Thu Aug 19 2021 Piotr Szubiakowski - 2.4.0~1.g2cd1a5b8-2
- make busybox a runtime dependency
- remove init files
- crete /nix/var structure

* Fri Aug 13 2021 Piotr Szubiakowski - 2.4.0~1.g2cd1a5b8-1
- adjust upstream spec file
