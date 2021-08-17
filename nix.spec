%global nixbld_user nixbld
%global nixbld_group nixbld
%global git_sha 2cd1a5b8f31627a09ac34afcbb0f76e90606204f

Name:           nix
Version:        2.4.0~1.g2cd1a5b8
Release:        1%{?dist}
Summary:        Nix is a purely functional package manager

License:        LGPLv2+
URL:            https://nixos.org/nix
Source0:        https://github.com/NixOS/nix/archive/%{git_sha}.tar.gz
# Unsafe hack to make build pass on EL 7
# Probably nobody would notice it anyway ;-)
Patch0:         nix-2.4-el7-boost-version.patch

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
%if 0%{?el7}
BuildRequires:  centos-release-scl
BuildRequires:  devtoolset-9
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

%if 0%{?el7}
%patch0 -p1
%endif


%build
# Enalbe GCC 9 for RHEL
%if 0%{?el8}
export PATH=/opt/rh/gcc-toolset-9/root/usr/bin${PATH:+:${PATH}}
export MANPATH=/opt/rh/gcc-toolset-9/root/usr/share/man:${MANPATH}
export INFOPATH=/opt/rh/gcc-toolset-9/root/usr/share/info${INFOPATH:+:${INFOPATH}}
export PCP_DIR=/opt/rh/gcc-toolset-9/root
export LD_LIBRARY_PATH=/opt/rh/gcc-toolset-9/root/usr/lib64:${LD_LIBRARY_PATH}
export PKG_CONFIG_PATH=/opt/rh/gcc-toolset-9/root/usr/lib64/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}
%endif
%if 0%{?el7}
export PATH=/opt/rh/devtoolset-9/root/usr/bin${PATH:+:${PATH}}
export MANPATH=/opt/rh/devtoolset-9/root/usr/share/man:${MANPATH}
export INFOPATH=/opt/rh/devtoolset-9/root/usr/share/info${INFOPATH:+:${INFOPATH}}
export PCP_DIR=/opt/rh/devtoolset-9/root
export LD_LIBRARY_PATH=/opt/rh/devtoolset-9/root/usr/lib64:/opt/rh/devtoolset-9/root/usr/lib/gcc/x86_64-redhat-linux/9:${LD_LIBRARY_PATH}
export PKG_CONFIG_PATH=/opt/rh/devtoolset-9/root/usr/lib64/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}
export LDFLAGS="-l:libc++.a"
export CXXFLAGS="-static-libstdc++"
%endif

%if 0%{?rhel}
export GTEST_CFLAGS=" -I/usr/include/gtest"
export GTEST_LIBS=" -lgtest -lgtest_main"
%endif

%undefine _hardened_build

./bootstrap.sh
%configure --disable-doc-gen --localstatedir=/nix/var
make V=1 %{?_smp_mflags}


%install
# Enalbe GCC 9 for RHEL
%if 0%{?el8}
export PATH=/opt/rh/gcc-toolset-9/root/usr/bin${PATH:+:${PATH}}
export MANPATH=/opt/rh/gcc-toolset-9/root/usr/share/man:${MANPATH}
export INFOPATH=/opt/rh/gcc-toolset-9/root/usr/share/info${INFOPATH:+:${INFOPATH}}
export PCP_DIR=/opt/rh/gcc-toolset-9/root
export LD_LIBRARY_PATH=/opt/rh/gcc-toolset-9/root/usr/lib64:${LD_LIBRARY_PATH}
export PKG_CONFIG_PATH=/opt/rh/gcc-toolset-9/root/usr/lib64/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}
%endif
%if 0%{?el7}
export PATH=/opt/rh/devtoolset-9/root/usr/bin${PATH:+:${PATH}}
export MANPATH=/opt/rh/devtoolset-9/root/usr/share/man:${MANPATH}
export INFOPATH=/opt/rh/devtoolset-9/root/usr/share/info${INFOPATH:+:${INFOPATH}}
export PCP_DIR=/opt/rh/devtoolset-9/root
export LD_LIBRARY_PATH=/opt/rh/devtoolset-9/root/usr/lib64:/opt/rh/devtoolset-9/root/usr/lib/gcc/x86_64-redhat-linux/9:${LD_LIBRARY_PATH}
export PKG_CONFIG_PATH=/opt/rh/devtoolset-9/root/usr/lib64/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}
export LDFLAGS="-l:libc++.a"
export CXXFLAGS="-static-libstdc++ -static-libgcc"
%endif

make DESTDIR=%{buildroot} install
mkdir -p %{buildroot}/nix/store

# Remove RPATHs for check-rpaths
chrpath -d %{buildroot}/usr/bin/nix
chrpath -d %{buildroot}/usr/lib64/*.so

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
/nix


%files devel
%{_includedir}/nix
%{_libdir}/pkgconfig/*.pc


%changelog
* Fri Aug 13 2021 Piotr Szubiakowski - 2.4.0~1.g2cd1a5b8-1
- adjust upstream spec file
