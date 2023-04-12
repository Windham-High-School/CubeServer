#!/usr/bin/env bash
# Bumps the version to the semver specified in the first argument.

RELEASE=$1
git branch release-${RELEASE}
git checkout release-${RELEASE}
git merge develop
echo ${RELEASE} > version.txt
./clean
git commit -am "bumped version"
git push -u origin release-${VERSION}

git checkout develop
git pull
git merge release-${VERSION}
git push

echo PR a merge from release-${RELEASE} to main

