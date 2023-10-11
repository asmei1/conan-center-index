from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, apply_conandata_patches, export_conandata_patches
import os

class Fbow(ConanFile):
    name = "fbow"
    license = "MIT"
    description = "A C++ library for indexing and converting images into a bag-of-word representation."
    url = "https://github.com/Hexagon-HTC/fbow.git"
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    exports = "../../toolchains/iOS/ios.toolchain.cmake",  "../../toolchains/android/android_toolchain.cmake", \
        "../../toolchains/iOS/xcodebuild_wrapper.in"
    source_dir = "fbow"
    no_copy_source = True

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.compiler.rm_safe("runtime")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opencv/4.6.0")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_UTILS"] = "OFF"
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["CMAKE_BUILD_TYPE"] = self.settings.build_type
        tc.variables["CMAKE_CONFIGURATION_TYPES"] = self.settings.build_type
        tc.variables["CMAKE_VERBOSE_MAKEFILE"] = True

        if self.settings.os == "Android":
            tc.variables["ANDROID_NATIVE_API_LEVEL"] = "24"
            tc.variables["ANDROID_USE_LEGACY_TOOLCHAIN_FILE"] = False
            tc.variables["ANDROID_ABI"] = "arm64-v8a"
            tc.variables["ANDROID_USE_CLANG"] = True
        elif self.settings.os == "Linux":
            if self.settings.compiler == "clang":
                tc.variables["CMAKE_CXX_COMPILER"] = "clang++"
                tc.variables["CMAKE_C_COMPILER"] = "clang"
            elif self.settings.compiler == "gcc": # jetson
                tc.variables["USE_SSE3"] = False
                tc.variables["USE_AVX"] = False
            tc.variables["CMAKE_CXX_FLAGS_RELEASE"] = "-O3 -DNDEBUG"
            tc.variables["CMAKE_CXX_FLAGS_DEBUG"] = "-g -O0"
            tc.variables["CMAKE_C_FLAGS_RELEASE"] = "-O3 -DNDEBUG"
            tc.variables["CMAKE_C_FLAGS_DEBUG"] = "-g -O0"
            tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"
            tc.variables["CMAKE_CXX_FLAGS"] = "-DLINUX -pipe"
            tc.variables["CMAKE_C_FLAGS"] = "-DLINUX -pipe"
            tc.variables["CMAKE_EXE_LINKER_FLAGS"] = "-Wl,--enable-new-dtags,-rpath,\\$ORIGIN -fuse-ld=gold"
            tc.variables["CMAKE_MODULE_LINKER_FLAGS"] = "-Wl,--enable-new-dtags,-rpath,\\$ORIGIN -fuse-ld=gold"
            tc.variables["CMAKE_SHARED_LINKER_FLAGS"] = "-Wl,--enable-new-dtags,-rpath,\\$ORIGIN -fuse-ld=gold"

        elif self.settings.os == "iOS":
            tc.variables["CMAKE_CXX_FLAGS"] = "-std=c++17"
            tc.variables["CMAKE_TOOLCHAIN_FILE"] = os.path.join(self.source_folder, "ios.toolchain.cmake")
            tc.variables["CMAKE_OSX_ARCHITECTURES"] = "arm64" if self.settings.arch == "armv8" else "x86_64"
            tc.variables["CMAKE_OSX_SYSROOT"] = self.settings.os.sdk
        elif self.settings.os == "Macos":
            tc.variables["CMAKE_CXX_FLAGS"] = "-std=c++17"
            tc.variables["CMAKE_MACOSX_BUNDLE"] = "OFF"
            tc.variables["CMAKE_OSX_ARCHITECTURES"] = "arm64" if self.settings.arch == "armv8" else "x86_64"
            if self.options.shared:
                tc.variables["CMAKE_XCODE_ATTRIBUTE_CODE_SIGNING_REQUIRED"] = "OFF"
                tc.variables["CMAKE_MACOSX_BUNDLE"] = "ON"
                tc.variables["CMAKE_EXE_LINKER_FLAGS"] = "-Wl,-rpath,\@rpath"
                tc.variables["CMAKE_MODULE_LINKER_FLAGS"] = "-Wl,-rpath,\@rpath"
                tc.variables["CMAKE_SHARED_LINKER_FLAGS"] = "-Wl,-rpath,\@rpath"

        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        apply_conandata_patches(self)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        if not self.options.shared:
            self.copy("*.pdb", dst="lib", src="bin/Debug")
        else:
            self.copy("*.pdb", dst="bin", src="bin/Debug")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fbow")
        self.cpp_info.set_property("cmake_target_name", "fbow::fbow")

        self.cpp_info.libs = ["fbow"]
        self.cpp_info.libdirs = ["bin", "lib"]
        self.cpp_info.includedirs.append(
            os.path.join("include", "fbow")
            )
