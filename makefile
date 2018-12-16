all: info dist

info:
	@echo "Small Business Hack"
	@echo "Developed by Chia-Hua Kai Peng"
	@echo ""

clean:
	rm -rf dist

dist:
	rm -rf dist
	mkdir dist
	pipenv lock --requirements > requirements.txt
	pip3 install -r requirements.txt -t dist
	rsync -ax --exclude src/test src/. dist

.PHONY: all info dist clean