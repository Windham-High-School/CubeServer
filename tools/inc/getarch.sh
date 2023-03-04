#!/usr/bin/env bash

# echoes the architecture of the cpu- example outputs:
#    x86_64
#    incompatible
#    arm64v8
function getarch {
    case $(uname -m) in

    x86_64 | amd64)
        echo x86_64
        ;;

    aarch64)
        target_line=$(grep -m1 ^"architecture" /proc/cpuinfo)
        ARM_VERSION=${target_line##*: }
        echo -e "arm64v${ARM_VERSION}"
        ;;

    *)
        echo incompatible
        ;;

    esac
}
