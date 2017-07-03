.PHONY: html

all: dist/index.html dist/css/style.css

dist/index.html:
	html

include generated.mk

html: $(wildcard src/html/*.html) $(wildcard src/html/**/*.html) src/data/global.json
		python main.py html

dist/css/style.css: $(wildcard src/scss/*.scss)
	python main.py sass
