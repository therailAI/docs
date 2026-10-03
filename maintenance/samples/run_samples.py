#!/usr/bin/env python3
"""Run the documentation's code samples against a real local sandbox.

The samples are read from the MDX pages themselves, so a page cannot drift
from what was tested. Each step names a page, the n-th fenced block of a
language, and what its output must show. Example identifiers in a page
(execution, journey and receipt ids) are replaced with the ones the earlier
steps produced.

    RAIL=/path/to/rail \\
    RAIL_SANDBOX_IMAGE=ghcr.io/therailai/rail-sandbox:0.2 \\
    SDK_NPM=@therailai/sdk@0.2.0      (or a path to a packed .tgz) \\
    SDK_PIP=therail-sdk==0.2.0        (or a path to a wheel) \\
    python3 maintenance/samples/run_samples.py [--keep]

Needs Docker, Node.js 22.13+, Python 3.12+ and curl. Uses a throwaway HOME, so
it never touches the caller's profiles, and removes the sandbox it made.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAME = "rail-docs-samples"


def blocks(page, language):
    """The fenced code blocks of one language in an MDX page, in order."""
    text = (ROOT / page).read_text()
    found = re.findall(r"^\s*```" + re.escape(language) + r"[^\n]*\n(.*?)^\s*```", text, re.S | re.M)
    if not found:
        raise SystemExit(f"{page}: no {language} blocks")
    return [textwrap_dedent(b) for b in found]


def textwrap_dedent(block):
    lines = block.splitlines()
    indent = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
    return "\n".join(l[indent:] for l in lines) + "\n"


class Runner:
    def __init__(self, work, rail, keep):
        self.work, self.rail, self.keep = work, rail, keep
        self.home = work / "home"
        self.project = work / "acme-pay"
        self.home.mkdir(parents=True)
        self.env = {
            "PATH": f"{Path(rail).parent}:{os.environ['PATH']}",
            "HOME": str(self.home),
            "RAIL_SANDBOX_IMAGE": os.environ["RAIL_SANDBOX_IMAGE"],
            "NO_COLOR": "1",
        }
        self.ids = {}
        self.failures = 0

    def sh(self, script, cwd=None, env=None, check=True):
        result = subprocess.run(["bash", "-euo", "pipefail", "-c", script], cwd=cwd or self.project,
                                env={**self.env, **(env or {})}, capture_output=True, text=True, timeout=600)
        output = result.stdout + result.stderr
        if check and result.returncode != 0:
            raise RuntimeError(f"exit {result.returncode}\n{output[-3000:]}")
        return output

    def substitute(self, text):
        for kind, value in self.ids.items():
            text = re.sub(kind + r"_[0-9a-f]{32}", value, text)
        return text

    def capture(self, output):
        for kind in ("exe", "grt", "apr"):
            match = re.search(r"\b" + kind + r"_[0-9a-f]{32}\b", output)
            if match and kind not in self.ids:
                self.ids[kind] = match.group(0)

    def step(self, label, action, expect=()):
        try:
            output = action()
            missing = [pattern for pattern in expect if not re.search(pattern, output)]
            if missing:
                raise RuntimeError(f"output lacks {missing}\n{output[-3000:]}")
            print(f"ok    {label}")
            return output
        except Exception as error:  # noqa: BLE001 - every failure is reported the same way
            self.failures += 1
            print(f"FAIL  {label}\n{error}")
            return ""

    # Languages other than shell run as files in the project.
    def node(self, code, env):
        path = self.project / "sample.mts"
        path.write_text(code)
        return self.sh(f"node --experimental-strip-types --no-warnings {path}", env=env)

    def python(self, code, env):
        path = self.project / "sample.py"
        path.write_text(code)
        return self.sh(f"{self.work / 'venv/bin/python'} {path}", env=env)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep", action="store_true", help="leave the sandbox and work directory")
    args = parser.parse_args()
    rail = shutil.which(os.environ.get("RAIL", "rail"))
    if not rail:
        raise SystemExit("set RAIL to the rail CLI")
    work = Path(tempfile.mkdtemp(prefix="rail-docs-samples-"))
    r = Runner(work, rail, args.keep)
    sandbox = f"-name {NAME}"
    try:
        # SDKs, installed the way the pages say (from a release, or a pre-release artifact).
        r.project.mkdir()
        r.step("install the TypeScript SDK", lambda: r.sh(f"npm init -y >/dev/null && npm install --no-audit --no-fund {os.environ['SDK_NPM']}"))
        r.step("install the Python SDK", lambda: r.sh(f"python3 -m venv {work / 'venv'} && {work / 'venv/bin/pip'} install -q {os.environ['SDK_PIP']}", cwd=work))

        # Quickstart. Step 2's block runs `mkdir acme-pay && cd acme-pay`; run it from the parent.
        start = blocks("quickstart.mdx", "bash")[2].replace("rail sandbox up", f"rail sandbox up {sandbox}")
        r.step("quickstart: init and start the sandbox", lambda: r.sh(start.replace("mkdir acme-pay && cd acme-pay", "cd acme-pay"), cwd=work), [r"\[sandbox\] up", r"granted the agent"])
        curl = blocks("quickstart.mdx", "bash")[3].replace("rail sandbox ca", f"rail sandbox ca {sandbox}").replace("rail sandbox token", f"rail sandbox token {sandbox}")
        r.step("quickstart: first call", lambda: r.sh(curl), [r'"principal_id":"pri_', r'"tenant_id":"ten_'])
        out = r.step("quickstart: govern an action", lambda: r.sh(blocks("quickstart.mdx", "bash")[4]), [r"state\s+completed", r"verified\s+rec_"])
        r.capture(out)
        r.step("quickstart: held for approval", lambda: r.sh(blocks("quickstart.mdx", "bash")[5]), [r"state\s+awaiting_approval\s+APPROVAL_REQUIRED"])
        r.step("quickstart: export and verify the journey", lambda: r.sh(r.substitute(blocks("quickstart.mdx", "bash")[6])), [r"verify\s+PASS", r"Authority chain\s+PASS"])

        # Sandbox page: the same call through the sandbox CA.
        sandbox_curl = blocks("get-started/sandbox.mdx", "bash")[1].replace("rail sandbox ca", f"rail sandbox ca {sandbox}").replace("rail sandbox token", f"rail sandbox token {sandbox}")
        r.step("sandbox page: curl", lambda: r.sh(sandbox_curl), [r'"principal_id"'])

        def sdk_env():
            ca = r.sh(f"rail sandbox ca {sandbox}").strip()
            token = r.sh(f"rail sandbox token {sandbox}").strip()
            return {"NODE_EXTRA_CA_CERTS": ca, "RAIL_SANDBOX_CA": ca, "RAIL_TOKEN": token}

        r.step("TypeScript SDK: read your context", lambda: r.node(blocks("sdks/typescript.mdx", "typescript")[0], sdk_env()), [r"signed in as pri_", r"grt_[0-9a-f]{32} active"])
        r.step("Python SDK: read your context", lambda: r.python(blocks("sdks/python.mdx", "python")[0], sdk_env()), [r"signed in as pri_", r"grt_[0-9a-f]{32} active"])

        # Governed helpers: each on a fresh sandbox, so each spends a fresh first grant.
        for page, language, run in [("sdks/governed-typescript.mdx", "typescript", r.node), ("sdks/governed-python.mdx", "python", r.python)]:
            r.step(f"{page}: reset the sandbox", lambda: r.sh(f"rail sandbox reset {sandbox}"), [r"\[sandbox\] up"])
            r.step(f"{page}: run a simulated action", lambda page=page, language=language, run=run: run(blocks(page, language)[0], {"RAIL_OPERATION_ID": "opi_docs" + os.urandom(8).hex()}), [r"exe_[0-9a-f]{32}", r"(executed|verification_pending|completed)"])
    finally:
        if args.keep:
            print(f"kept: {work} and sandbox {NAME}")
        else:
            subprocess.run(["bash", "-c", f"rail sandbox down {sandbox} >/dev/null 2>&1; docker rm -fv {NAME} >/dev/null 2>&1; docker volume rm {NAME} >/dev/null 2>&1"], env=r.env)
            shutil.rmtree(work, ignore_errors=True)
    print(f"\ndocs samples: {'all passed' if not r.failures else f'{r.failures} failed'}")
    sys.exit(1 if r.failures else 0)


if __name__ == "__main__":
    main()
