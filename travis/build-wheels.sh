#!/bin/bash
set -e -u -x

function repair_wheel {
    wheel="$1"
    if ! auditwheel show "$wheel"; then
        echo "Skipping non-platform wheel $wheel"
    else
        auditwheel repair "$wheel" --plat "$PLAT" -w /io/wheelhouse/
    fi
}


# Install a system package required by our library
#yum install -y atlas-devel

# Compile wheels
/opt/python/cp35-35mu/bin/pip install -r /io/dev-requirements.txt
/opt/python/cp35-35mu/bin/pip wheel /io/ --no-deps -w wheelhouse/

/opt/python/cp36-36mu/bin/pip install -r /io/dev-requirements.txt
/opt/python/cp36-36mu/bin/pip wheel /io/ --no-deps -w wheelhouse/

/opt/python/cp37-37mu/bin/pip install -r /io/dev-requirements.txt
/opt/python/cp37-37mu/bin/pip wheel /io/ --no-deps -w wheelhouse/

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    repair_wheel "$whl"
done

# Install packages and test

/opt/python/cp35-35mu/bin/pip install python-manylinux-demo --no-index -f /io/wheelhouse
(cd "$HOME";  "/opt/python/cp35-35mu/nosetests" pymanylinuxdemo)

/opt/python/cp36-36mu/bin/pip install python-manylinux-demo --no-index -f /io/wheelhouse
(cd "$HOME";  "/opt/python/cp36-36mu/nosetests" pymanylinuxdemo)

/opt/python/cp37-37mu/bin/pip install python-manylinux-demo --no-index -f /io/wheelhouse
(cd "$HOME";  "/opt/python/cp37-37mu/nosetests" pymanylinuxdemo)

