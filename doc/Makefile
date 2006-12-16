.PHONY: all publish

all: felo-de.pdf felo-de/index.html felo-de.html felo-de-handbuch.zip

publish: all
	scp -rp *.png felo-de felo-de.html felo-de.pdf felo-de-handbuch.zip \
	  felo.sourceforge.net:/home/groups/f/fe/felo/htdocs/

felo-de-handbuch.zip: felo-de/index.html
	zip -9 -r felo-de-handbuch felo-de

felo-de/index.html: felo-de.texi
	LC_ALL=de_DE ; makeinfo --html --css-include=felo.css felo-de.texi
	cp *.png felo-de/

felo-de.html: felo-de.texi
	LC_ALL=de_DE ; makeinfo --html --css-include=felo.css --no-split felo-de.texi

felo-de.pdf: felo-de.ltx felo-de-t2l.cfg
	pdflatex felo-de.ltx
	pdflatex felo-de.ltx
# 	bash makeindex.bat
# 	pdflatex felo-de.ltx

felo-de.ltx: felo-de.texi
	LC_ALL=de_DE ; ./texi2latex felo-de global-options=12pt document-class=scrbook
