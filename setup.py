import os
import re
import sys
import sysconfig
import platform
import subprocess

from distutils.version import LooseVersion
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: " +
                ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)',
                                                   out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name)))
        # cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
        #              '-DPYTHON_EXECUTABLE=' + sys.executable]

        cmake_args = []

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(
                cfg.upper(),
                extdir)]
            if sys.maxsize > 2 ** 32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + "Debug"]  # cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''),
            self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        subprocess.check_call(
            ['ls', ext.sourcedir],
            cwd=self.build_temp,
            env=env
        )

        subprocess.check_call(
            ['cmake', ext.sourcedir] + cmake_args,
            cwd=self.build_temp,
            env=env
        )
        subprocess.check_call(['cmake', '--build', '.'] + build_args,
                              cwd=self.build_temp)
        print()  # Add an empty line for cleaner output


setup(
    name="RocketJoe",  # Replace with your own username
    version="1.0.0",
    athor="Example Author",
    author_email="cuberduckninja@gmail.com",
    # packages=find_packages(),
    description='An example cmake extension module',
    long_description=open("./README.md", 'r').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cyberduckninja/RocketJoe",
    keywords="test, cmake, extension",
    classifiers=["Intended Audience :: Developers",
                 "License :: OSI Approved :: "
                 "GNU Lesser General Public License v3 (LGPLv3)",
                 "Natural Language :: English",
                 "Programming Language :: C",
                 "Programming Language :: C++",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 3.6",
                 "Programming Language :: Python :: Implementation :: CPython"],
    license='MIT',
    cmdclass=dict(build_ext=CMakeBuild),
    ext_modules=[CMakeExtension('RocketJoe')],
    # zip_safe=False,
)
