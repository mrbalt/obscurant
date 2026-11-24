#!/bin/sh
# Front-end edits do not change the build, and dev builds read symlinked files, so Firefox keeps
# serving old compiled scripts from the profile cache, even after a plain restart.
# The .purgecaches marker (what "make" leaves behind) makes the next start, however it is
# launched, throw those caches away. Run after any front-end change.
for d in "$HOME/Projects/browser/src/obj-pgo-use/dist/bin/browser" "$HOME/Projects/browser/src/obj-v1/dist/bin/browser"; do
  [ -d "$d" ] && touch "$d/.purgecaches"
done
echo purge marker updated
