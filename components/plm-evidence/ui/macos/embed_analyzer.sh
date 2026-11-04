#!/bin/sh
set -eu
source_binary="${AETHEL_INSTALLED_ANALYZER_BINARY:-$HOME/.local/share/aethel-code-analyzer/releases/7e3e38c39d07/aethel_code_analyzer}"
expected='42c678e9ae31697167ba8f3da50b4b69369274eab9bf11dff5f6b8d27a5cdd43'
helper="$TARGET_BUILD_DIR/$CONTENTS_FOLDER_PATH/MacOS/aethel_code_analyzer"
manifest="$TARGET_BUILD_DIR/$UNLOCALIZED_RESOURCES_FOLDER_PATH/analyzer.sha256"
rm -f "$helper" "$manifest"
if [ ! -f "$source_binary" ]; then
  echo 'warning: installed pinned CodeAnalyzer unavailable; in-app analysis will be unavailable'
  exit 0
fi
actual=$(/usr/bin/shasum -a 256 "$source_binary" | /usr/bin/awk '{print $1}')
if [ "$actual" != "$expected" ]; then
  echo 'error: installed CodeAnalyzer does not match pinned release digest' >&2
  exit 1
fi
mkdir -p "$(dirname "$helper")" "$(dirname "$manifest")"
/bin/cp "$source_binary" "$helper"
/usr/bin/codesign --force --sign "${EXPANDED_CODE_SIGN_IDENTITY:--}" --entitlements "$PROJECT_DIR/analyzer-helper.entitlements" "$helper"
/usr/bin/shasum -a 256 "$helper" | /usr/bin/awk '{print $1}' > "$manifest"
