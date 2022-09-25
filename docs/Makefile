# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS     ?=
SPHINXBUILD    ?= sphinx-build
SPHINXAPIDOC   ?= sphinx-apidoc
RM             ?= rm
SOURCEDIR      = source
BUILDDIR       = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	@$(RM) -r "$(SOURCEDIR)"
	@$(RM) -r "$(BUILDDIR)"

.PHONY: clean help Makefile

apidoc:
	@$(SPHINXAPIDOC) ../src/CubeServer-app/cubeserver_app/ -o "$(SOURCEDIR)"
	@$(SPHINXAPIDOC) ../src/CubeServer-api/cubeserver_api/ -o "$(SOURCEDIR)"
	@$(SPHINXAPIDOC) ../src/CubeServer-common/cubeserver_common/ -o "$(SOURCEDIR)"

build:
#	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(0)
	@$(SPHINXBUILD) "$(SOURCEDIR)/../" "$(BUILDDIR)" $(SPHINXOPTS)

%: clean build
