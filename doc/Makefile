.PHONY: all publish

all: api/index.html \
	  felo.pdf felo/index.html felo.html felo-manual.zip \
	  felo-de.pdf felo-de/index.html felo-de.html felo-de-handbuch.zip

publish: all
	rsync --rsh=ssh -avuz \
	  *.png felo.css translations.html api \
	  felo felo.html felo.pdf felo-manual.zip \
	  felo-de felo-de.html felo-de.pdf felo-de-handbuch.zip \
	  felo.sourceforge.net:/home/groups/f/fe/felo/htdocs/
	rsync --rsh=ssh -avuz \
	  homepage.html felo.sourceforge.net:/home/groups/f/fe/felo/htdocs/index.html

api/index.html: ../src/felo_rating.py
	cd ..; mv src felo; cd felo; epydoc --config epydoc.cfg; cd ..; mv felo src


# English

felo-manual.zip: felo/index.html
	zip -9 -r felo-manual felo

felo/index.html: felo.texi
	LC_ALL=de_DE ; makeinfo --html --css-include=felo.css felo.texi
	cp *.png felo.css felo/

felo.html: felo.texi
	LC_ALL=de_DE ; makeinfo --html --css-include=felo.css --no-split felo.texi

felo.pdf: felo.ltx felo-t2l.cfg
	pdflatex felo.ltx
	pdflatex felo.ltx
# 	bash makeindex.bat
# 	pdflatex felo.ltx

felo.ltx: felo.texi
	LC_ALL=de_DE ; ./texi2latex felo global-options=12pt document-class=scrbook


# German

felo-de-handbuch.zip: felo-de/index.html
	zip -9 -r felo-de-handbuch felo-de

felo-de/index.html: felo-de.texi
	LC_ALL=de_DE ; makeinfo --html --css-include=felo.css felo-de.texi
	cp *.png felo.css felo-de/

felo-de.html: felo-de.texi
	LC_ALL=de_DE ; makeinfo --html --css-include=felo.css --no-split felo-de.texi

felo-de.pdf: felo-de.ltx felo-de-t2l.cfg
	pdflatex felo-de.ltx
	pdflatex felo-de.ltx
# 	bash makeindex.bat
# 	pdflatex felo-de.ltx

felo-de.ltx: felo-de.texi
	LC_ALL=de_DE ; ./texi2latex felo-de global-options=12pt document-class=scrbook
