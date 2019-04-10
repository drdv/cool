PYTHON=python3
VENV_NAME=.venv

all:
	@echo "Check available targets ..."

interpreter:
	wget http://www.cs.virginia.edu/~cs415/cool/osx-x86/cool -O cool_interpreter
	chmod +x cool_interpreter

.PHONY: setup-venv
setup-venv:
	${PYTHON} -m venv ${VENV_NAME} && \
	. ${VENV_NAME}/bin/activate && \
	pip install --upgrade pip && \
	pip install -r .requirements.txt

.PHONY: test
test:
	py.test -v utest
