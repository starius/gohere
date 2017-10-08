#!/bin/bash
# Dependencies: bash coreutils wget tar sed gcc make
set -xue
rm -rf '/tmp/sia-build'
T1=$(mktemp -d)
T2=$(mktemp -d)
wget -O "${T2}/go1.4-bootstrap-20170531.tar.gz" "https://storage.googleapis.com/golang/go1.4-bootstrap-20170531.tar.gz"
echo "49f806f66762077861b7de7081f586995940772d29d4c45068c134441a743fa2  ${T2}/go1.4-bootstrap-20170531.tar.gz" | sha256sum --check --strict -
tar -C "${T2}" -xzf "${T2}/go1.4-bootstrap-20170531.tar.gz"
if [ -f "${T2}/go/include/libc.h" ]; then sed "s/struct timespec {/struct timespec_disabled_by_gohere {/g" -i "${T2}/go/include/libc.h"; fi
find "${T2}/go" -name "*.c" -print0 | xargs -0 -I cfile sed "s/(vlong)~0 << 32/(uvlong)~0 << 32/g" -i cfile
cd "${T2}/go/src" && GOROOT_FINAL="${T1}/go1.4-bootstrap-20170531_bootstrap" GOROOT_BOOTSTRAP="" ./make.bash | grep "Installed Go"
mkdir -p "${T1}/go1.4-bootstrap-20170531_bootstrap"
cp -a "${T2}/go/src" "${T2}/go/bin" "${T2}/go/pkg" "${T2}/go/misc" "${T2}/go/include" "${T1}/go1.4-bootstrap-20170531_bootstrap"
rm -rf "${T2}"
wget -O "${T1}/go1.9.1.src.tar.gz" "https://storage.googleapis.com/golang/go1.9.1.src.tar.gz"
echo "a84afc9dc7d64fe0fa84d4d735e2ece23831a22117b50dafc75c1484f1cb550e  ${T1}/go1.9.1.src.tar.gz" | sha256sum --check --strict -
tar -C "${T1}" -xzf "${T1}/go1.9.1.src.tar.gz"
if [ -f "${T1}/go/include/libc.h" ]; then sed "s/struct timespec {/struct timespec_disabled_by_gohere {/g" -i "${T1}/go/include/libc.h"; fi
find "${T1}/go" -name "*.c" -print0 | xargs -0 -I cfile sed "s/(vlong)~0 << 32/(uvlong)~0 << 32/g" -i cfile
cd "${T1}/go/src" && GOROOT_FINAL="/tmp/sia-build/goroot" GOROOT_BOOTSTRAP="${T1}/go1.4-bootstrap-20170531_bootstrap" ./make.bash | grep "Installed Go"
mkdir -p "/tmp/sia-build/goroot"
cp -a "${T1}/go/src" "${T1}/go/bin" "${T1}/go/pkg" "${T1}/go/misc" "/tmp/sia-build/goroot"
rm -rf "${T1}"

export PATH="/tmp/sia-build/goroot/bin:${PATH}"
export GOPATH='/tmp/sia-build/gopath'

cd '/tmp/sia-build/'
wget -O '/tmp/sia-build/42ec283fb59f9f71dfb95b03005916776a7ea5f0.tar.gz' https://github.com/NebulousLabs/Sia/archive/42ec283fb59f9f71dfb95b03005916776a7ea5f0.tar.gz
echo "312b061e2d36ed586d40602c0502e4480652e6ef404812705ebab2e0eb2fca60  /tmp/sia-build/42ec283fb59f9f71dfb95b03005916776a7ea5f0.tar.gz" | sha256sum --check --strict -
mkdir -p "${GOPATH}/src/github.com/NebulousLabs"
tar -C "${GOPATH}/src/github.com/NebulousLabs" -xzf /tmp/sia-build/42ec283fb59f9f71dfb95b03005916776a7ea5f0.tar.gz
mv "${GOPATH}/src/github.com/NebulousLabs"/Sia-42ec283fb59f9f71dfb95b03005916776a7ea5f0 "${GOPATH}/src/github.com/NebulousLabs"/Sia
for goos in darwin linux windows; do
    for goarch in 386 amd64; do
        GOOS="$goos" GOARCH="$goarch" make -C "${GOPATH}/src/github.com/NebulousLabs"/Sia release-std
    done
done
hostbin="/tmp/sia-build/gopath/bin/$(go env GOHOSTOS)_$(go env GOHOSTARCH)/"
mkdir -p "$hostbin"
mv /tmp/sia-build/gopath/bin/{siac,siad} "$hostbin"
sha256sum /tmp/sia-build/gopath/bin/*/{siac,siad}*
