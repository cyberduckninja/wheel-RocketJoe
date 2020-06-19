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
/opt/python/cp36-cp36m/bin/pip install -r /io/dev-requirements.txt

ln -s /opt/python/cp36-cp36m/bin/conan /usr/bin/conan

conan remote add bincrafters https://api.bintray.com/conan/bincrafters/public-conan
conan remote add jinncrafters https://api.bintray.com/conan/jinncrafters/conan
conan profile new default --detect
conan profile update settings.compiler.libcxx=libstdc++11 default
echo $(ls /io)
conan install \
             -b missing \
             -b boost \
             -b fmt \
             -b spdlog \
             -b botan \
             -b libsodium \
             -s build_type=Debug \
             -s compiler.libcxx=libstdc++11 \
             .

rm /usr/bin/cmake

ln -s /opt/python/cp36-cp36m/bin/cmake /usr/bin/cmake


/opt/python/cp36-cp36m/bin/pip wheel /io/ --no-deps -w wheelhouse/



# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    repair_wheel "$whl"
done

# Install packages and test

/opt/python/cp36-cp36m/bin/pip install python-manylinux-demo --no-index -f /io/wheelhouse
(cd "$HOME";  "/opt/python/cp36-cp36m/nosetests" pymanylinuxdemo)


