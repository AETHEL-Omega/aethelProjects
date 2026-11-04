import Cocoa
import FlutterMacOS
import CryptoKit

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
      case "analyzeProject":
        guard let arguments = call.arguments as? [String: Any],
              let expected = arguments["path"] as? String, !expected.isEmpty else {
          result(FlutterError(code: "invalid_project", message: "Projektpfad fehlt", details: nil)); return
        }
        guard let executable = Bundle.main.url(forAuxiliaryExecutable: "aethel_code_analyzer"),
              let bytes = try? Data(contentsOf: executable, options: [.mappedIfSafe]),
              let manifest = Bundle.main.url(forResource: "analyzer", withExtension: "sha256"),
              let releaseURL = Bundle.main.url(forResource: "analyzer", withExtension: "release"),
              let release = try? String(contentsOf: releaseURL, encoding: .utf8).trimmingCharacters(in: .whitespacesAndNewlines),
              !release.isEmpty,
              let expectedDigest = try? String(contentsOf: manifest, encoding: .utf8).trimmingCharacters(in: .whitespacesAndNewlines),
              expectedDigest.count == 64,
              SHA256.hash(data: bytes).map({ String(format: "%02x", $0) }).joined() == expectedDigest else {
          result(FlutterError(code: "analyzer_unavailable", message: "Freigegebener Analyzer ist nicht paketiert oder stimmt nicht überein.", details: nil)); return
        }
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true; panel.canChooseFiles = false; panel.allowsMultipleSelection = false
        panel.prompt = "Projekt für Analyse freigeben"
        panel.message = "Wähle die angezeigte Arbeitskopie aus. Der Analyzer liest nur dieses Projekt."
        panel.begin { response in
          guard response == .OK, let selected = panel.url else { result(nil); return }
          guard selected.resolvingSymlinksInPath().standardizedFileURL.path == URL(fileURLWithPath: expected).resolvingSymlinksInPath().standardizedFileURL.path else {
            result(FlutterError(code: "project_mismatch", message: "Ausgewählter Ordner entspricht nicht der Arbeitskopie.", details: nil)); return
          }
          guard selected.startAccessingSecurityScopedResource() else {
            result(FlutterError(code: "project_access_denied", message: "Projektzugriff nicht freigegeben.", details: nil)); return
          }
          DispatchQueue.global(qos: .utility).async {
            defer { selected.stopAccessingSecurityScopedResource() }
            let process = Process()
            let output = Pipe()
            process.executableURL = executable
            process.arguments = ["--path", selected.path, "--format", "aix", "--max-entries", "10000", "--max-files", "1000", "--max-bytes", "8388608", "--max-file-bytes", "524288", "--max-findings", "100"]
            process.standardOutput = output; process.standardError = FileHandle.nullDevice
            let deadline = DispatchWorkItem { if process.isRunning { process.terminate() } }
            do {
              try process.run()
              DispatchQueue.global(qos: .utility).asyncAfter(deadline: .now() + 60, execute: deadline)
              var collected = Data(); var exceeded = false
              while true {
                let chunk = output.fileHandleForReading.readData(ofLength: 65536)
                if chunk.isEmpty { break }
                if collected.count + chunk.count > 2_000_000 { exceeded = true; if process.isRunning { process.terminate() }; break }
                collected.append(chunk)
              }
              process.waitUntilExit(); deadline.cancel()
              let data = String(data: collected, encoding: .utf8)
              DispatchQueue.main.async {
                if exceeded || process.terminationStatus != 0 || data == nil {
                  result(FlutterError(code: "analysis_failed", message: "Analyse fehlgeschlagen oder begrenzt; kein Ergebnis übernommen.", details: nil))
                } else { result(["report": data!, "release": release]) }
              }
            } catch {
              deadline.cancel()
              DispatchQueue.main.async { result(FlutterError(code: "analysis_unavailable", message: "Analyzer konnte in der App-Sandbox nicht gestartet werden.", details: nil)) }
            }
          }
        }
      default: result(FlutterMethodNotImplemented)
      }
    }
    super.awakeFromNib()
  }
}
