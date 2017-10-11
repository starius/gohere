#!/bin/bash
# Dependencies: bash coreutils wget tar sed gcc make
set -xue
T1="/tmp/goroot/T1"
mkdir -p "$T1"
T2="${T1}/go1.4-bootstrap-20170531_bootstrap/T2"
T0="${T1}/second"
mkdir -p "$T2"
mkdir -p "$T0"
wget -O "${T2}/go1.4-bootstrap-20170531.tar.gz" "https://storage.googleapis.com/golang/go1.4-bootstrap-20170531.tar.gz"
echo "49f806f66762077861b7de7081f586995940772d29d4c45068c134441a743fa2  ${T2}/go1.4-bootstrap-20170531.tar.gz" | sha256sum --check --strict -
tar -C "${T2}" -xzf "${T2}/go1.4-bootstrap-20170531.tar.gz"
sed -i.bak -e "s/struct timespec {/struct timespec_disabled_by_gohere {/g" -- "${T2}/go/include/libc.h"
find "${T2}/go" -name "*.c" -print0 | xargs -0 -I cfile sed -i.bak -e "s/(vlong)~0 << 32/(uvlong)~0 << 32/g" -- cfile
cd "${T2}/go/src" && GOROOT_FINAL="${T1}/go1.4-bootstrap-20170531_bootstrap" GOROOT_BOOTSTRAP="" ./make.bash | grep "Installed Go"
mkdir -p "${T1}/go1.4-bootstrap-20170531_bootstrap"
cp -a "${T2}/go/src" "${T2}/go/bin" "${T2}/go/pkg" "${T2}/go/misc" "${T2}/go/include" "${T1}/go1.4-bootstrap-20170531_bootstrap"
rm -rf "$T2"
wget -O "${T1}/go1.9.1.src.tar.gz" "https://storage.googleapis.com/golang/go1.9.1.src.tar.gz"
echo "a84afc9dc7d64fe0fa84d4d735e2ece23831a22117b50dafc75c1484f1cb550e  ${T1}/go1.9.1.src.tar.gz" | sha256sum --check --strict -
tar -C "${T1}" -xzf "${T1}/go1.9.1.src.tar.gz"
find "${T1}/go" -name "*.c" -print0 | xargs -0 -I cfile sed -i.bak -e "s/(vlong)~0 << 32/(uvlong)~0 << 32/g" -- cfile
cd "${T1}/go/src" && GOROOT_FINAL="/tmp/goroot" GOROOT_BOOTSTRAP="${T1}/go1.4-bootstrap-20170531_bootstrap" ./make.bash | grep "Installed Go"
mkdir -p "/tmp/goroot"
cp -a "${T1}/go/src" "${T1}/go/bin" "${T1}/go/pkg" "${T1}/go/misc" "/tmp/goroot"
tar -C "${T0}" -xzf "${T1}/go1.9.1.src.tar.gz"
find "${T0}/go" -name "*.c" -print0 | xargs -0 -I cfile sed -i.bak -e "s/(vlong)~0 << 32/(uvlong)~0 << 32/g" -- cfile
cd "${T0}/go/src" && GOROOT_FINAL="/tmp/goroot" GOROOT_BOOTSTRAP="/tmp/goroot" ./make.bash | grep "Installed Go"
mkdir -p "/tmp/goroot2"
cp -a "${T0}/go/src" "${T0}/go/bin" "${T0}/go/pkg" "${T0}/go/misc" "/tmp/goroot2"
rm -rf "$T1"

cd /tmp

export GOPATH='/tmp/gopath'

mkdir -p "${GOPATH}/src/test"
cat > "${GOPATH}/src/test"/main.go << EOF
package main

import "os"
import "os/signal"

func main() {
    sig := make(chan os.Signal, 10)
    signal.Stop(sig)
}
EOF
for goos in darwin linux windows; do
    for goarch in 386 amd64; do
        CGO_ENABLED=1 GOOS="$goos" GOARCH="$goarch" /tmp/goroot2/bin/go install -a -tags netgo -ldflags='-s -w' test
    done
done
hostbin="/tmp/gopath/bin/$(/tmp/goroot2/bin/go env GOHOSTOS)_$(/tmp/goroot2/bin/go env GOHOSTARCH)/"
mkdir -p "$hostbin"
mv /tmp/gopath/bin/test "$hostbin"
sha256sum /tmp/gopath/bin/*/test*