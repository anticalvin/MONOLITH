#!/bin/zsh
set -e
root=$(cd "$(dirname "$0")" && pwd)
read "photo?Photo path: "
read "url?HTTP(S) URL: "
read "consent?Type YES to allow QArt URL-fragment modification: "
[[ "$consent" = YES ]] || exit 0
out="$root/research/user_results/$(date +%Y%m%d-%H%M%S)"
python3 "$root/research/generate_portrait.py" "$photo" "$url" "$out" --confirm-fragment-modification
open "$out/index.html"
