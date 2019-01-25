sudo apt-get install -y cython libc6-armel-cross libc6-dev-armel-cross binutils-arm-linux-gnueabi libncurses5-dev

wget http://security.debian.org/debian-security/pool/updates/main/p/python2.7/libpython2.7-dev_2.7.9-2+deb8u2_armel.deb
dpkg -x libpython2.7-dev_2.7.9-2+deb8u2_armel.deb libpython2.7-dev_2.7.9-2+deb8u2_armel_ext
sudo cp -r libpython2.7-dev_2.7.9-2+deb8u2_armel_ext/usr/include/arm-linux-gnueabi/ /usr/local/include/
rm -r libpython2.7-dev_2.7.9-2+deb8u2_armel*

wget http://security.debian.org/debian-security/pool/updates/main/p/python2.7/libpython2.7-dev_2.7.9-2+deb8u2_armhf.deb
dpkg -x libpython2.7-dev_2.7.9-2+deb8u2_armhf.deb libpython2.7-dev_2.7.9-2+deb8u2_armhf_ext
sudo cp -r libpython2.7-dev_2.7.9-2+deb8u2_armhf_ext/usr/include/arm-linux-gnueabihf/ /usr/local/include/
rm -r libpython2.7-dev_2.7.9-2+deb8u2_armhf*

cp compile_pyfiles.sh auth.py gen_key.sh gen_makefile.py "$1"
cd "$1"

echo ""
echo "use ./compile_pyfiles.sh <main python file name> to compile."
echo ""