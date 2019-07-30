Name:		python-sz-daemon
Version: 	0.1
Release: 	1%{?dist}.sz
Summary: 	Класс реализующий демона на Python
Group: 		common
License: 	commercial
URL:		http://www.fintech.ru
Source0:	%{name}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

#%global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib;")
%global python_sitelib /usr/lib/python2.7/site-packages

%description
Класс реализующий демона на Python

%prep

%setup -n %{name} -q

%install
mkdir -p %{buildroot}/%{python_sitelib}/python_sz_daemon/
cp -r ./lib/* %{buildroot}/%{python_sitelib}/python_sz_daemon/

#mkdir -p %{buildroot}/usr/share/python_sz_daemon/
#cp -r ./share/* %{buildroot}/usr/share/python_sz_daemon/

%clean
rm -rf %{buildroot}

%post

%files
%defattr(644,root,root,-)
%{python_sitelib}/python_sz_daemon/base_daemon.py
%{python_sitelib}/python_sz_daemon/daemon_configurator.py
%{python_sitelib}/python_sz_daemon/__init__.py
#/usr/share/python_sz_daemon/example.py


%exclude %{python_sitelib}/python_sz_daemon/*.pyc
%exclude %{python_sitelib}/python_sz_daemon/*.pyo
#%exclude /usr/share/python_sz_daemon/*.pyc
#%exclude /usr/share/python_sz_daemon/*.pyo

%doc

%changelog
* Tue Jun 18 2019 Deyneko Aleksey <deyneko@fintech.ru> 0.1-0
- Первая версия
