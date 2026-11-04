#!/bin/sh
set -eu
source_library="$PROJECT_DIR/../../flutter_bridge/rust/target/aarch64-apple-darwin/release/libaethel_evidence_bridge.dylib"
target_library="$TARGET_BUILD_DIR/$CONTENTS_FOLDER_PATH/Frameworks/libaethel_evidence_bridge.dylib"
rm -f "$target_library"
if [ ! -f "$source_library" ]; then
  echo 'warning: native evidence bridge is not built; raw case assessment will be unavailable'
  exit 0
fi
mkdir -p "$(dirname "$target_library")"
/bin/cp "$source_library" "$target_library"
/usr/bin/install_name_tool -id @rpath/libaethel_evidence_bridge.dylib "$target_library"
/usr/bin/codesign --force --sign "${EXPANDED_CODE_SIGN_IDENTITY:--}" "$target_library"
