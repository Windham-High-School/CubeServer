#!/bin/sh

envsubst </mediamtx.yml | sponge /mediamtx.yml

echo STARTING MEDIAMTX
/mediamtx
echo MEDIAMTX DONE KICKED THE BUCKET.
echo WAH WAH.
