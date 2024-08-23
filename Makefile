# Minimal makefile for Sphinx documentation
#
ifeq (, $(shell which dot))
 $(error "No dot in $(PATH), consider doing apt install graphviz")
endif

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = soderstrom-rikardgithubio
SOURCEDIR     = source
BUILDDIR      = build
ENVDIR        = ${BUILDDIR}/.venv

# Put it first so that "make" without argument is like "make help".
help: ${ENVDIR}
	@(. ${ENVDIR}/bin/activate && $(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O))

.PHONY: help Makefile

${ENVDIR}:
	python3 -m venv ${ENVDIR}
	(. ${ENVDIR}/bin/activate && pip install -r requirements.txt)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile ${ENVDIR}
	@(. ${ENVDIR}/bin/activate && $(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O))
