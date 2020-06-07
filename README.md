# gohere

[![Travis build][travis-badge]][travis-page]
[![AppVeyor build][appveyor-badge]][appveyor-page]
[![License][license]](LICENSE)

[license]: https://img.shields.io/badge/License-MIT-brightgreen.png
[travis-page]: https://travis-ci.org/starius/gohere
[travis-badge]: https://travis-ci.org/starius/gohere.png
[appveyor-page]: https://ci.appveyor.com/project/starius/gohere
[appveyor-badge]: https://ci.appveyor.com/api/projects/status/e5ti0kc3rgdohhyx?svg=true

Install Go into a local directory:

```
$ ./gohere.py ~/.goroot
```

`~/.goroot` is a directory where Go will be installed.
You can choose a different directory, of course.

You need `gcc` package.

To start using the installed Go, add the following to
`~/.bashrc`

```
export PATH=$HOME/.goroot/bin:$PATH
```

Also remember to set GOPATH. I use my home directory as GOPATH:

```
export GOPATH=$HOME
```

Optional arguments:

```
  -h, --help            show this help message and exit
  --update-versions     Update list of Go verions instead of normal operation
                        (default: False)
  --echo                Produce shell code instead (default: False)
  --echo-goroot ECHO_GOROOT
                        Hardcoded GOROOT for --echo (default: None)
  --version VERSION     Go version (default: latest)
  --cache CACHE         Cache for downloaded Go sources (default:
                        /home/ff/.cache/gohere)
  --test                Enable Go tests (takes several minutes to complete)
                        (default: False)
  --race {yes,no,auto}  Whether to build std with -race (default: auto)
```
