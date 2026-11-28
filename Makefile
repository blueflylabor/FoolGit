# ==============================================================================
# FoolGit Makefile
# Convenient build and deployment shortcuts for developers.
# ==============================================================================

.PHONY: help cli gui all install uninstall clean test

help:
	@echo "FoolGit Build & Deployment Commands:"
	@echo "  make cli       - Build standalone lightweight CLI binary (dist/foolgit)"
	@echo "  make gui       - Build standalone macOS desktop app (dist/FoolGit.app)"
	@echo "  make all       - Build both CLI and GUI"
	@echo "  make install   - Run installer (install.sh)"
	@echo "  make uninstall - Run uninstaller (uninstall.sh)"
	@echo "  make test      - Run automated core tests"
	@echo "  make clean     - Clean build and dist directories"

cli:
	chmod +x scripts/build_cli.sh
	./scripts/build_cli.sh

gui:
	chmod +x scripts/build_macos.sh
	./scripts/build_macos.sh

all: cli gui

install:
	chmod +x install.sh
	./install.sh

uninstall:
	chmod +x uninstall.sh
	./uninstall.sh

test:
	python3 -m unittest discover -s tests -v

clean:
	rm -rf build dist *.spec
