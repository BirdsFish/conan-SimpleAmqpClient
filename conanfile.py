from conans import ConanFile, CMake, tools
import os


class SimpleAmqpClientConan(ConanFile):
    name = "SimpleAmqpClient"
    version = "2.5.1"
    license = "MIT"
    description = "SimpleAmqpClient is an easy-to-use C++ wrapper around the rabbitmq-c C library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=True", "fPIC=True"
    requires = ("rabbitmq-c/0.10.0@", ("zlib/1.2.11", "override"), "boost/1.73.0@")
    generators = "cmake", "cmake_find_package"

    @property
    def src_dir(self):
        return "%s-%s" % (self.name, self.version)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("shared")
            self.options.remove("fPIC")

    def configure(self):
        if self.settings.os != "Windows" and self.options.shared:
            self.options["boost"].fPIC = True

    def source(self):
        url = "https://github.com/alanxz/SimpleAmqpClient.git"
        self.run("git clone %s %s" % (url, self.src_dir))
        self.run("cd %s && git checkout %s" % (self.src_dir, "f9fb520011477b3bc512defb99e0b0f598d76870"))
        cmakelist_tst = os.path.join(self.src_dir, "CMakeLists.txt")
        tools.replace_in_file(cmakelist_tst, "project(SimpleAmqpClient LANGUAGES CXX)",
                              """project(SimpleAmqpClient LANGUAGES CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()""")
        tools.replace_in_file(cmakelist_tst, "set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/Modules)",
                "list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/Modules)")
        tools.replace_in_file(cmakelist_tst, "find_package(Rabbitmqc REQUIRED)",
                                            "find_package(rabbitmq-c REQUIRED)")
        os.unlink("%s/Modules/FindRabbitmqc.cmake" % self.src_dir)
        tools.replace_in_file(cmakelist_tst, "${Rabbitmqc_SSL_ENABLED}", "ON")

    def build(self):
        cmake = CMake(self)
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        else:
            cmake.definitions['BUILD_SHARED_LIBS'] = True
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = "install"
        cmake.configure(source_folder=self.src_dir)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*.h", dst=".", src="install")
        self.copy("*.lib", dst="lib", src="install", keep_path=False)
        self.copy("*.dll", dst="bin", src="install", keep_path=False)
        self.copy("*.pdb", dst="bin", src="install", keep_path=False)
        self.copy("*.so*", dst="lib", src="install", keep_path=False, symlinks=True)
        self.copy("*.dylib", dst="lib", src="install", keep_path=False, symlinks=True)
        self.copy("*.a", dst="lib", src="install", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = [self.name+".2"]
        else:
            self.cpp_info.libs = [self.name]
