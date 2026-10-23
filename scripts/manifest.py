"""只读生成归档清单；输出到 stdout，不创建或覆盖归档。"""
import hashlib, json, sys
from pathlib import Path

def manifest(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("归档根目录必须是实际目录")
    excluded = {".git", "__pycache__", ".DS_Store", "06-同步记录.md", "sync-state.json", "SHA256SUMS.json", "回读", "node_modules", ".env"}
    files = []
    def visit(folder):
        for p in sorted(folder.iterdir()):
            if p.name in excluded:
                continue
            if p.is_symlink():
                raise ValueError("拒绝符号链接: " + str(p))
            if p.is_dir():
                visit(p)
            elif p.is_file():
                h = hashlib.sha256()
                with p.open("rb") as f:
                    for chunk in iter(lambda: f.read(1024 * 1024), b""):
                        h.update(chunk)
                files.append({"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "sha256": h.hexdigest()})
    visit(root)
    return {"algorithm": "SHA-256", "files": files}

if __name__ == "__main__":
    print(json.dumps(manifest(sys.argv[1]), ensure_ascii=False, indent=2))
