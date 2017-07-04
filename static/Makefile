.PHONY: html

all: dist/mac-1/index.html dist/mac-2/index.html dist/css/style.css

dist/mac-1/index.html: $(wildcard src/html/modules/*.html) src/html/mac-1.html src/data/global.json
	make html

dist/mac-2/index.html: $(wildcard src/html/modules/*.html) src/html/mac-2.html src/data/global.json
	make html

html:
	python main.py html

dist/css/style.css: $(wildcard src/scss/*.scss)
	python main.py sass

launch:
	bash -c 'while [ 0 ]; do make;sleep 1;done'
