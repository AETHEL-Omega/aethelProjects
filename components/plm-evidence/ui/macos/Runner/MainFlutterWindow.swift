import Cocoa
import FlutterMacOS

class MainFlutterWindow: NSWindow {
  private var inventoryDirectory: URL?
  private let inventoryBookmarkKey = "projects.inventory.directory.bookmark.v1"

  private func bindInventoryDirectory(_ url: URL) -> Bool {
    guard url.startAccessingSecurityScopedResource() else { return false }
    inventoryDirectory?.stopAccessingSecurityScopedResource()
    inventoryDirectory = url
    return true
  }

  override func awakeFromNib() {
    let flutterViewController = FlutterViewController()
    let windowFrame = self.frame
    self.contentViewController = flutterViewController
    self.setFrame(windowFrame, display: true)

    RegisterGeneratedPlugins(registry: flutterViewController)
    let channel = FlutterMethodChannel(name: "aethel.projects.inventory/v1", binaryMessenger: flutterViewController.engine.binaryMessenger)
    channel.setMethodCallHandler { [weak self] call, result in
      guard let self = self else { result(FlutterError(code: "window_unavailable", message: nil, details: nil)); return }
      switch call.method {
      case "restoreDirectory":
        guard let bookmark = UserDefaults.standard.data(forKey: self.inventoryBookmarkKey) else { result(nil); return }
        do {
          var stale = false
          let url = try URL(resolvingBookmarkData: bookmark, options: [.withSecurityScope], relativeTo: nil, bookmarkDataIsStale: &stale)
          guard !stale, self.bindInventoryDirectory(url) else {
            result(FlutterError(code: "inventory_permission_expired", message: "Ordner erneut auswählen", details: nil)); return
          }
          result(url.path)
        } catch { result(FlutterError(code: "inventory_bookmark_invalid", message: "Ordner erneut auswählen", details: nil)) }
      case "chooseDirectory":
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        panel.allowsMultipleSelection = false
        panel.prompt = "Inventurordner auswählen"
        panel.begin { response in
          guard response == .OK, let url = panel.url else { result(nil); return }
          do {
            guard self.bindInventoryDirectory(url) else {
              result(FlutterError(code: "inventory_permission_denied", message: "Ordner nicht freigegeben", details: nil)); return
            }
            let bookmark = try url.bookmarkData(options: [.withSecurityScope, .securityScopeAllowOnlyReadAccess], includingResourceValuesForKeys: nil, relativeTo: nil)
            UserDefaults.standard.set(bookmark, forKey: self.inventoryBookmarkKey)
            result(url.path)
          } catch { result(FlutterError(code: "inventory_bookmark_failed", message: "Ordnerzugriff konnte nicht gespeichert werden", details: nil)) }
        }
      default: result(FlutterMethodNotImplemented)
      }
    }
    super.awakeFromNib()
  }
}
