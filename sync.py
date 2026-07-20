"""
GitHub 同步脚本
用法：
    python sync.py                     # 自动 add + commit + push，commit message 带时间戳
    python sync.py "更新了单词表"        # 自定义 commit message
    python sync.py --dry-run           # 预览将要同步的文件，不实际推送
"""
import subprocess
import sys
import os
from datetime import datetime

# ========== 配置 ==========
REPO_DIR = r"C:\Users\mqf0205\Desktop\english"      # 仓库路径
GIT_EXE  = r"C:\Program Files\Git\bin\git.exe"       # git.exe 完整路径
REMOTE   = "origin"
BRANCH   = "master"
# ==========================


def git(*args):
    """运行 git 命令，返回 (returncode, stdout, stderr)"""
    cmd = [GIT_EXE, "-C", REPO_DIR] + list(args)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def main():
    # 解析参数
    dry_run = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    message = args[0] if args else f"Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # 1. 检查仓库状态
    code, out, err = git("status", "--porcelain")
    if code != 0:
        print(f"[✗] git status 失败: {err}")
        sys.exit(1)

    if not out:
        print("[✓] 没有变动，无需同步。")
        return

    print(f"待同步文件:\n{out}\n")

    if dry_run:
        print("[dry-run] 以上文件将被同步，实际未推送。")
        return

    # 2. git add .
    code, _, err = git("add", ".")
    if code != 0:
        print(f"[✗] git add 失败: {err}")
        sys.exit(1)
    print("[✓] git add .")

    # 3. git commit
    code, _, err = git("commit", "-m", message)
    if code != 0:
        # 可能是 "nothing to commit"
        print(f"[!] git commit: {err}")
    else:
        print(f"[✓] git commit -m \"{message}\"")

    # 4. git push
    print("[→] git push ...")
    code, out, err = git("push", REMOTE, BRANCH)
    if code != 0:
        print(f"[✗] git push 失败:\n{err}")
        # 尝试给出建议
        if "403" in err or "remote: Invalid username or password" in err or "Authentication" in err:
            print("\n[TIP] 认证失败，可能是 Token 过期。请运行以下命令重新设置：")
            print('  git config --global credential.helper manager')
        sys.exit(1)
    print(f"[✓] 推送成功!\n{out}")


if __name__ == "__main__":
    main()
