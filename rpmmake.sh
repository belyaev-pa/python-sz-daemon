#!/bin/bash
echo "[START]"
specfile_name=$(find . -name '*.spec')
echo "[SPEC]=$specfile_name"
rm -rf /root/rpmbuild/*
mkdir -p /root/rpmbuild/SPECS
cp $specfile_name /root/rpmbuild/SPECS

mkdir -p /root/rpmbuild/SOURCES
cur_dir_name=${PWD##*/}
echo "[CUR_DIR_NAME]=$cur_dir_name"
src_tar_name="/root/rpmbuild/SOURCES/$cur_dir_name.tar.gz"
echo "[SRC TAR NAME]=$src_tar_name"
tar --exclude='.git' --exclude='.gitignore' -cf $src_tar_name ../$cur_dir_name
echo "[BUILD]"
rpmbuild -ba /root/rpmbuild/SPECS/$specfile_name
echo "[DONE BUILD]"
mkdir -p /root/RPMS/$cur_dir_name
mkdir -p /root/SRPMS/$cur_dir_name
for rpm_file_name in $(find /root/rpmbuild/RPMS/ -name '*.rpm'); do cp $rpm_file_name /root/RPMS/$cur_dir_name; done
for srpm_file_name in $(find /root/rpmbuild/SRPMS/ -name '*.rpm'); do cp $srpm_file_name /root/SRPMS/$cur_dir_name; done
echo "[DONE]"
echo "Version 2.0"

