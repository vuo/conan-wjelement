from conans import ConanFile, CMake, tools
import platform

class WJElementConan(ConanFile):
    name = 'wjelement'

    source_version = '1.3'
    package_version = '1'
    version = '%s-%s' % (source_version, package_version)

    build_requires = 'llvm/3.3-5@vuo/stable', \
               'vuoutils/1.0@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/netmail-open/wjelement'
    license = 'https://github.com/netmail-open/wjelement/blob/master/COPYING'
    description = 'A library for validating JSON schema'
    source_dir = 'wjelement-%s' % source_version
    build_dir = '_build'
    install_dir = '_install'
    libs = {
        'wjelement': 1,
        'wjreader': 1,
        'wjwriter': 1,
        'xpl': 1,
    }
    generators = 'cmake'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://github.com/netmail-open/wjelement/archive/v%s.tar.gz' % self.source_version,
                  sha256='63f588777e5cee58e17206e454aa5ab46486e27f416b3b92aba098896472ee56')

        self.run('mv %s/COPYING.LESSER %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        import VuoUtils
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake = CMake(self)

            cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
            cmake.definitions['CMAKE_C_COMPILER']   = self.deps_cpp_info['llvm'].rootpath + '/bin/clang'
            cmake.definitions['CMAKE_C_FLAGS'] = '-Oz -DNDEBUG'
            cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64'
            cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.10'
            cmake.definitions['CMAKE_INSTALL_PREFIX'] = '../%s' % self.install_dir

            cmake.configure(source_dir='../%s' % self.source_dir,
                            build_dir='.')
            cmake.build()
            cmake.install()
        with tools.chdir('%s/lib' % self.install_dir):
            VuoUtils.fixLibs(self.libs, self.deps_cpp_info)

    def package(self):
        self.copy('*.h', src='%s/include' % self.install_dir, dst='include/wjelement')

        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        for f in list(self.libs.keys()):
            self.copy('lib%s.%s' % (f, libext), src='%s/lib' % self.install_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = list(self.libs.keys())
        self.cpp_info.includedirs = ['include', 'include/wjelement']
