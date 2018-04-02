from conans import ConanFile, CMake, tools
import os
import platform

class WJElementConan(ConanFile):
    name = 'wjelement'

    source_version = '1.2'
    package_version = '3'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-2@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/netmail-open/wjelement'
    license = 'https://github.com/netmail-open/wjelement/blob/master/COPYING'
    description = 'A library for validating JSON schema'
    source_dir = 'wjelement-%s' % source_version
    build_dir = '_build'
    install_dir = '_install'
    libs = ['wjelement', 'wjreader', 'wjwriter', 'xpl']
    generators = 'cmake'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.9@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://github.com/netmail-open/wjelement/archive/v%s.tar.gz' % self.source_version,
                  sha256='5568d0cfcbeaca232bb61c2aeaf8860b4e8f09f9cccacb9adf3e4bc8de989d5f')

    def fixId(self, library):
        if platform.system() == 'Darwin':
            self.run('install_name_tool -id @rpath/lib%s.dylib lib%s.dylib' % (library, library))
            self.run('install_name_tool -rpath %s @loader_path lib%s.dylib' % (os.getcwd(), library))
        elif platform.system() == 'Linux':
            patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
            self.run('%s --set-soname lib%s.so lib%s.so' % (patchelf, library, library))
            self.run('%s --remove-rpath lib%s.so' % (patchelf, library))
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

    def fixRefs(self, library):
        if platform.system() == 'Darwin':
            self.run('install_name_tool -change %s/libwjreader.1.dylib @rpath/libwjreader.dylib lib%s.dylib' % (os.getcwd(), library))
            self.run('install_name_tool -change %s/libwjwriter.1.dylib @rpath/libwjwriter.dylib lib%s.dylib' % (os.getcwd(), library))
            self.run('install_name_tool -change %s/libxpl.1.dylib @rpath/libxpl.dylib lib%s.dylib' % (os.getcwd(), library))
        elif platform.system() == 'Linux':
            patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
            self.run('%s --replace-needed libwjreader.so.1 libwjreader.so lib%s.so' % (patchelf, library))
            self.run('%s --replace-needed libwjwriter.so.1 libwjwriter.so lib%s.so' % (patchelf, library))
            self.run('%s --replace-needed libxpl.so.1 libxpl.so lib%s.so' % (patchelf, library))
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

    def build(self):
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
            for f in self.libs:
                self.fixId(f)
                self.fixRefs(f)

    def package(self):
        self.copy('*.h', src='%s/include' % self.install_dir, dst='include/wjelement')

        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        for f in self.libs:
            self.copy('lib%s.%s' % (f, libext), src='%s/lib' % self.install_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = self.libs
        self.cpp_info.includedirs = ['include', 'include/wjelement']
