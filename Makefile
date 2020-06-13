##
# ##
# zhaires
#
# @file
# @version 0.0.1

# find python3
PYTHON=`/usr/bin/which python3`

# our testing targets
.PHONY: tests flake black isort all clean

all: mypy isort black flake tests clean

tests:
	${PYTHON} -m pytest --cov=zhaires tests

flake:
	${PYTHON} -m flake8 zhaires

black:
	${PYTHON} -m black -t py37 zhaires tests

isort:
	${PYTHON} -m isort --atomic -rc -y zhaires tests

mypy:
	${PYTHON} -m mypy zhaires

clean:
	$(RM) Aires.status
	$(RM) Aires.dirs


# end
