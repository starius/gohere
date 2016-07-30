#!/bin/bash

set -xue

unset GOROOT

for version in \
    1.2.2 \
    1.3 1.3.1 1.3.2 1.3.3 \
    1.4 1.4.1 1.4.2 1.4.3 \
    1.5 1.5.1 1.5.2 1.5.3 1.5.4 \
    1.6 1.6.1 1.6.2 1.6.3 \
; do \
    rm -rf goroot$version gopath$version

    # inctall
    ./gohere.py \
        goroot$version \
        --version=$version
    goroot$version/bin/go env

    # build and and run hello
    mkdir gopath$version
    GOPATH=$(pwd)/gopath$version goroot$version/bin/go \
        get github.com/golang/example/hello
    gopath$version/bin/hello
done
