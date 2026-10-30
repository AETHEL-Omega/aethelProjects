from aethel_projects.stubs import scan


def test_language_stubs_and_exclusions(tmp_path):
    files = {
        'app.py': 'from typing import Protocol, overload\nfrom abc import abstractmethod\nclass P(Protocol):\n def method(self): ...\nclass A:\n @abstractmethod\n def f(self): pass\n@overload\ndef f(x: int): ...\ndef pending(): pass\ndef missing():\n raise NotImplementedError\n',
        'src/lib.rs': 'fn x() { todo!(); }\nfn y() { unimplemented!(); }\n',
        'src/App.swift': 'func f() { fatalError("not implemented") }\n',
        'src/a.dart': 'void f() { throw UnimplementedError(); }\n',
        'src/a.ts': 'function f() { throw new Error("not implemented"); }\n',
        'src/a.js': '// TODO: implement this\n',
        'tests/test_fake.py': 'def fake(): pass\n',
        'vendor/a.rs': 'todo!()\n',
        'build/a.rs': 'todo!()\n',
        'src/generated.rs': '// @generated\ntodo!()\n',
    }
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    findings = scan(tmp_path)
    assert sum(f['path'] == 'app.py' for f in findings) == 2
    assert {f['path'] for f in findings} == {'app.py', 'src/lib.rs', 'src/App.swift', 'src/a.dart', 'src/a.ts', 'src/a.js'}
    assert all(f['line'] > 0 and f['sicherheit'] in {'sicher', 'hinweis'} for f in findings)
    assert all(f['sicherheit'] == 'sicher' for f in findings if f['path'] == 'app.py')
