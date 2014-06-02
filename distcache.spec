
Summary: Distributed SSL session cache
Name: distcache
Version: 1.4.5
Release: 23
License: LGPLv2
Group: System Environment/Daemons
URL: http://www.distcache.org/
Source0: http://downloads.sourceforge.net/distcache/%{name}-%{version}.tar.gz
Patch0: distcache-1.4.5-setuid.patch
Patch1: distcache-1.4.5-libdeps.patch
Patch2: distcache-1.4.5-limits.patch
Source1: dc_server.init
Source2: dc_client.init
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: automake >= 1.7, autoconf >= 2.50, libtool, openssl-devel
Requires(post): /sbin/chkconfig, /sbin/ldconfig, shadow-utils
Requires(preun): /sbin/service, /sbin/chkconfig

%description
The distcache package provides a variety of functionality for
enabling a network-based session caching system, primarily for
(though not restricted to) SSL/TLS session caching.

%package devel
Group: Development/Libraries
Summary: Development tools for distcache distributed session cache
Requires: distcache = %{version}-%{release}

%description devel
This package includes the libraries that implement the necessary
network functionality, the session caching protocol, and APIs for
applications wishing to use a distributed session cache, or indeed
even to implement a storage mechanism for a session cache server.

%prep
%setup -q
%patch0 -p1 -b .setuid
%patch1 -p1 -b .libdeps
%patch2 -p1 -b .limits

%build
libtoolize --force --copy && aclocal && autoconf
automake -aic --gnu || : automake ate my hamster
pushd ssl
autoreconf -i || : let it fail too
popd
%configure --enable-shared --disable-static
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
make -C ssl install DESTDIR=$RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
install -p -m 755 $RPM_SOURCE_DIR/dc_server.init \
        $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/dc_server
install -p -m 755 $RPM_SOURCE_DIR/dc_client.init \
        $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/dc_client

mkdir -p $RPM_BUILD_ROOT%{_sbindir}

# Unpackaged files
rm -f $RPM_BUILD_ROOT%{_bindir}/{nal_test,piper} \
      $RPM_BUILD_ROOT%{_libdir}/lib*.la

%post
/sbin/chkconfig --add dc_server
/sbin/chkconfig --add dc_client
/sbin/ldconfig

%preun
if [ $1 = 0 ]; then
    /sbin/service dc_server stop > /dev/null 2>&1
    /sbin/service dc_client stop > /dev/null 2>&1
    /sbin/chkconfig --del dc_server
    /sbin/chkconfig --del dc_client
fi

%postun -p /sbin/ldconfig

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_bindir}/sslswamp
%{_bindir}/dc_*
%{_sysconfdir}/rc.d/init.d/dc_*
%doc ANNOUNCE CHANGES README LICENSE FAQ
%{_libdir}/*.so.*
%{_mandir}/man1/*
%{_mandir}/man8/*
%{_datadir}/swamp

%files devel
%defattr(-,root,root,-)
%{_includedir}/distcache
%{_includedir}/libnal
%{_libdir}/*.so
%{_mandir}/man2/*
