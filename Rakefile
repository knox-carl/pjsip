# encoding: utf-8

require 'rake'
require 'rake/clean'
ARCHS             = [:arm64, :armv7, :armv7s, :i386]
MODULE_DIRS       = %W[pjlib pjsip third_party pjlib-util pjmedia pjnath]
LIB_DIRS          = MODULE_DIRS.map { |m| File.join(m, 'lib') }
DEVPATH           = `xcode-select -p`.strip
SIMULATOR_DEVPATH = File.join(DEVPATH, 'Platforms/iPhoneSimulator.platform/Developer')

# TODO: cache dirs
def dirs_for_arch(arch)
  arch = arch.to_s
  LIB_DIRS.map  { |lib| File.join(lib, arch) }
          .each { |dir| directory dir }
end

def move_build_products(arch)
  arch = arch.to_s
  LIB_DIRS.each do |dir|
    FileList[File.join(dir, '*.a')].each do |product|
      target = File.join(product.pathmap('%d'), arch)
      mv product, target, :force => true
    end
  end
end

desc "Build arm64 static libraries"
task :arm64 => dirs_for_arch(:arm64) do
  sh 'ARCH="-arch arm64" ./configure-iphone'
  sh 'make dep && make clean && make'
  move_build_products(:arm64)
end
CLEAN.include(dirs_for_arch(:arm64))

desc "Build i386 static libraries"
task :i386 => dirs_for_arch(:i386) do
  sh <<-CMD
    DEVPATH=#{SIMULATOR_DEVPATH}\
    CFLAGS="-O2 -m32 -miphoneos-version-min=5.0"\
    LDFLAGS="-O2 -m32 -miphoneos-version-min=5.0"\
    ARCH="-arch i386"\
    ./configure-iphone
  CMD
  sh 'make dep && make clean && make'
  move_build_products(:i386)
end
CLEAN.include(dirs_for_arch(:i386))

desc "Build armv7 static libraries"
task :armv7 => dirs_for_arch(:armv7) do
  sh 'ARCH="-arch armv7" ./configure-iphone'
  sh 'make dep && make clean && make'
  move_build_products(:armv7)
end
CLEAN.include(dirs_for_arch(:armv7))

desc "Build armv7s static libraries"
task :armv7s => dirs_for_arch(:armv7s) do
  sh 'ARCH="-arch armv7s" ./configure-iphone'
  sh 'make dep && make clean && make'
  move_build_products(:armv7s)
end
CLEAN.include(dirs_for_arch(:armv7s))

desc "Build all supported arch"
task :build_all => ARCHS

LIB_DIRS.each do |lib|
  FileList[File.join(lib, 'i386', '*a')].each do |archive|
    CLOBBER.include(archive.pathmap('%{i386/,}p'))
  end
end

desc "Build fat archive"
task :archive do
  LIB_DIRS.each do |lib|
    FileList[File.join(lib, 'i386', '*a')].each do |archive|
      as = FileList[archive.pathmap('%{i386,*}p')]
      args = as.map { |a| "-arch #{a.pathmap('%-1d')} #{a}" }.join(' ')
      output = archive.pathmap('%{i386/,}p')
      sh "lipo #{args} -create -output #{output}"
      cp output, './lib'
    end
  end
end

task :ios => [:build_all, :archive]
task :default => :ios
