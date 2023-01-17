%define		crates_ver	0.9.0

Summary:	A login manager daemon
Name:		greetd
Version:	0.9.0
Release:	1
License:	GPL v3+
Group:		Applications
Source0:	https://git.sr.ht/~kennylevinsen/greetd/archive/%{version}.tar.gz
# Source0-md5:	af714594386b3e648f20d6d923d2357d
Source1:	%{name}-crates-%{crates_ver}.tar.xz
# Source1-md5:	fed2be39ae7d934cad15a5e4443ddb4e
Source2:	%{name}.pamd
URL:		https://git.sr.ht/~kennylevinsen/greetd
BuildRequires:	cargo
BuildRequires:	pam-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 2.011
BuildRequires:	rust
BuildRequires:	scdoc
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/useradd
Requires:	/bin/sh
Requires:	greetd(greeter)
Provides:	user(greetd-greeter)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
greetd is a minimal and flexible login manager daemon that makes no
assumptions about what you want to launch.

%package greeter-agreety
Summary:	Simple, text-based greeter for greetd
Requires:	%{name} = %{version}-%{release}
Provides:	greetd(greeter)

%description greeter-agreety
Simple, text-based greeter for greetd.

%prep
%setup -q -a1

%{__mv} %{name}-%{crates_ver}/* .
sed -i -e 's/@@VERSION@@/%{version}/' Cargo.lock

export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >.cargo/config <<EOF
[source.crates-io]
registry = 'https://github.com/rust-lang/crates.io-index'
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/vendor'
EOF

%build
export CARGO_HOME="$(pwd)/.cargo"
%cargo_build --frozen

%{__make} -C man

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/etc/{greetd,pam.d},%{_bindir},%{systemdunitdir},/var/lib/greetd}

cp -p %{cargo_objdir}/{greetd,agreety} $RPM_BUILD_ROOT%{_bindir}
sed -e 's/^\([#[:space:]]*\)\?user[[:space:]]*=.*/user = greetd-greeter/' config.toml > $RPM_BUILD_ROOT/etc/greetd/config.toml
cp -p greetd.service $RPM_BUILD_ROOT%{systemdunitdir}
cp -p %{SOURCE2} $RPM_BUILD_ROOT/etc/pam.d/greetd

%{__make} -C man install \
	DESTDIR=$RPM_BUILD_ROOT \
	MANDIR=%{_mandir}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%useradd -u 343 -r -d /var/lib/greetd -s /bin/sh -c "greetd greeter user" -g nobody -G video greetd-greeter

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
if [ "$1" = "0" ]; then
	%userremove greetd-greeter
fi
%systemd_reload

%files
%defattr(644,root,root,755)
%doc README.md
%dir /etc/greetd
%config(noreplace) %verify(not md5 mtime size) /etc/greetd/config.toml
%config(noreplace) %verify(not md5 mtime size) /etc/pam.d/greetd
%attr(755,root,root) %{_bindir}/%{name}
%{systemdunitdir}/%{name}.service
%{_mandir}/man1/greetd.1*
%{_mandir}/man5/greetd.5*
%{_mandir}/man7/greetd-ipc.7*
%attr(750,greetd-greeter,root) %dir /var/lib/greetd

%files greeter-agreety
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/agreety
%{_mandir}/man1/agreety.1*
