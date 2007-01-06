.PHONY: update

all: de.gmo fr.gmo

%.gmo : %.po
	cd ../src ; xgettext --output=../po/felo.pot felo.py felo_rating.py
	msgmerge --update $< felo.pot
	msgfmt --output-file=$@ $<
	mkdir -p `basename $@ .gmo`
	cp $@ `basename $@ .gmo`/felo.mo
