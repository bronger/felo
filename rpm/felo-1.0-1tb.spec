# RedHat spec file

Summary: Calculates Felo ratings for estimating sport fencers.
Name: felo
Version: 1.0
Release: 1tb
Copyright: MIT License
Group: Applications/Sports
#Source: 
url: http://felo.sourceforge.net
BuildRoot: %{_tmppath}/%{name}-root
Requires: python >= 2.4

%description
Felo ratings are a wonderful new way to estimate fencers.  The Felo
program calculates these ratings for a given group of fencers.  The
only thing the user needs to do is to provide the program with a
bout result list.

The program offers a graphical user interface (using wxWidgets).

%prep
%setup -n felo-1.0-linux

%build
rm -rf %{buildroot}
make LOCAL=""

%install
make LOCAL="" ROOT="$RPM_BUILD_ROOT" install

%clean
rm -Rf %{buildroot}

%post
echo "Fertig"

%preun
if [ -e "%{_datadir}/xml/tbook/script_created" ] ; then
  rm -f %{_datadir}/xml/tbook/script_created ;
  rm -f %{_bindir}/saxon ;
fi

%postun
%{texhash}

%files
%defattr(-, root, root)
%doc COPYING README WHATSNEW
%{_bindir}/felo
%{_datadir}/felo
%{_datadir}/doc/felo
%{_infodir}/felo.info.gz
%{_infodir}/screenshot1.png

%changelog
* Mon Nov 22 2002 Torsten Bronger 
- Initial RPM generation (no release yet).
