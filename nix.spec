%global nixbld_user nixbld
%global nixbld_group nixbld
%global git_sha 2cd1a5b8f31627a09ac34afcbb0f76e90606204f

Name:           nix
Version:        2.4.0~1.g2cd1a5b8
Release:        1%{?dist}
Summary:        Nix is a purely functional package manager

License:        LGPLv2+
URL:            https://nixos.org/nix
%undefine       _disable_source_fetch
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
BuildRequires:  gcc-c++
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
%setup -n %{name}-%{git_sha}


%build
./bootstrap.sh
%undefine _hardened_build
%configure --disable-doc-gen --localstatedir=/nix/var
make %{?_smp_mflags}


%install
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
