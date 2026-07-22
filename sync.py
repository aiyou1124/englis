
"""
GitHub 同步脚本
用法：
    python sync.py                     # 自动 add + commit + push，commit message 带时间戳
    python sync.py "更新了单词表"        # 自定义 commit message
    python sync.py --dry-run           # 预览将要同步的内容，不实际推送
"""
import subprocess
import sys
from datetime import datetime

# ========== 配置 ==========
REPO_DIR = r"C:\Users\mqf0205\Desktop\english"
GIT_EXE  = r"C:\Program Files\Git\bin\git.exe"
REMOTE   = "origin"
BRANCH   = "master"
# ==========================


def git(*args):
    """运行 git 命令，返回 (returncode, stdout, stderr)"""
    cmd = [GIT_EXE, "-C", REPO_DIR] + list(args)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def do_push():
    """推送并处理错误"""
    print("[>>>] git push ...")
    code, out, err = git("push", REMOTE, BRANCH)
    if code != 0:
        print(f"[FAIL] git push 失败:\n{err}")
        if "403" in err or "Invalid username" in err or "Authentication" in err:
            print("\n[TIP] 认证失败，可能是 Token 过期。")
        sys.exit(1)
    print(f"[OK] 推送成功!\n{out}")


def check_unpushed():
    """返回本地领先远程的 commit 数量"""
    code, out, _ = git("rev-list", "--count", f"{REMOTE}/{BRANCH}..HEAD")
    if code == 0 and out.isdigit():
        return int(out)
    return 0


def main():
    dry_run = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    message = args[0] if args else f"Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # 1. 检查文件变动
    code, porcelain, err = git("status", "--porcelain")
    if code != 0:
        print(f"[FAIL] git status 失败: {err}")
        sys.exit(1)

    has_changes = bool(porcelain)

    # 2. 检查未推送的 commits
    unpushed = check_unpushed()
    has_unpushed = unpushed > 0

    if not has_changes and not has_unpushed:
        print("[OK] 没有变动，无需同步。")
        return

    if dry_run:
        if has_changes:
            print(f"待同步文件:\n{porcelain}\n")
        if has_unpushed:
            print(f"待推送 commits: {unpushed} 个\n")
        print("[DRY-RUN] 以上将被同步，实际未推送。")
        return

    # 3. 文件变动 → add + commit
    if has_changes:
        print(f"待同步文件:\n{porcelain}\n")

        code, _, err = git("add", ".")
        if code != 0:
            print(f"[FAIL] git add 失败: {err}")
            sys.exit(1)
        print("[OK] git add .")

        code, _, err = git("commit", "-m", message)
        if code != 0:
            print(f"[!] git commit: {err}")
        else:
            print(f"[OK] git commit -m \"{message}\"")
    else:
        print(f"无文件变动，但本地有 {unpushed} 个 commit 未推送。")

    # 4. 推送
    do_push()


if __name__ == "__main__":
    main()
