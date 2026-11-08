# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Fail-closed Windows candidate download policy, without fetching model weights."""

from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest



WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/pc-suite-embedded-model.yml"


def fetch_contract():
    job = WORKFLOW.read_text(encoding="utf-8").split("  evaluate-cpu-backend:\n", 1)[1]
    step = job.split("      - name: Fetch Unsloth", 1)[1].split("      - name:", 1)[0]
    script = textwrap.dedent(step.split("        run: |\n", 1)[1])
    downloader = script.split("function Receive-PublicAsset(", 1)[1].split("\n$url = ", 1)[0]
    return job, step, script, downloader


def assert_one_larger_but_bounded_budget_covers_all_assets_and_retries():
    job, step, script, downloader = fetch_contract()
    assert "    timeout-minutes: 75\n" in job
    assert "        timeout-minutes: 35\n" in step
    assert script.count("$downloadDeadline =") == 1
    assert "$downloadDeadline = [System.Threading.CancellationTokenSource]::new([TimeSpan]::FromMinutes(30))" in script
    assert script.index("$downloadDeadline =") < script.index("function Receive-PublicAsset(")
    assert "FromMinutes(15)" not in downloader
    assert "$client.Timeout = [System.Threading.Timeout]::InfiniteTimeSpan" in downloader
    assert "CreateLinkedTokenSource($downloadDeadline.Token)" in downloader
    assert downloader.count("$operation.CancelAfter([TimeSpan]::FromSeconds(60))") == 2
    assert re.search(r"GetAsync\(.+ResponseHeadersRead, \$operation.Token\)", downloader)
    assert "ReadAsync($buffer, 0, $buffer.Length, $operation.Token)" in downloader
    assert "$downloadDeadline.Dispose()" in script


def assert_transient_retries_are_finite_clean_and_do_not_reuse_signed_urls():
    _, _, _, downloader = fetch_contract()
    assert "for ($attempt = 1; $attempt -le 3; $attempt++)" in downloader
    assert downloader.index("$uri = [Uri]$url") > downloader.index("for ($attempt")
    assert "$status -in @(408, 429, 500, 502, 503, 504)" in downloader
    assert '$phase -in @("headers", "read")' in downloader
    assert "-not $retryable -or $attempt -eq 3 -or $downloadDeadline.IsCancellationRequested" in downloader
    assert "$downloadDeadline.Token.WaitHandle.WaitOne([TimeSpan]::FromSeconds(5 * $attempt))" in downloader
    assert "[System.IO.FileMode]::CreateNew" in downloader
    assert "if ($created -and -not $succeeded) { Remove-Item -LiteralPath $destination -Force }" in downloader
    for resource in ("outputStream", "inputStream", "response", "operation", "client"):
        assert f"${resource}.Dispose()" in downloader
    assert "received $total bytes" in downloader
    assert "Artifact download failed on attempt $attempt in $phase after $total bytes" in downloader


def assert_every_redirect_is_manually_validated_before_network_access():
    _, _, _, downloader = fetch_contract()
    assert "$handler.AllowAutoRedirect = $false" in downloader
    assert "for ($redirect = 0; $redirect -le 5; $redirect++)" in downloader
    guard = downloader.split('if ($uri.Scheme', 1)[1].split("$operation.CancelAfter", 1)[0]
    for condition in (
        '-cne "https"', "$uri.Port -ne 443", '$uri.UserInfo -ne ""',
        '$uri.Host -eq "huggingface.co"', '$uri.Host.EndsWith(".huggingface.co")',
        '$uri.Host.EndsWith(".hf.co")', '@("apache.org", "www.apache.org")',
    ):
        assert condition in guard
    assert 'throw "Public artifact redirect escaped' in guard
    assert "$redirect -eq 5 -or $null -eq $response.Headers.Location" in downloader
    assert "$uri = [Uri]::new($uri, $response.Headers.Location)" in downloader
    assert downloader.index('if ($uri.Scheme') < downloader.index("$client.GetAsync")


def assert_streaming_sizes_candidate_hash_and_acceptance_still_fail_closed():
    job, step, script, downloader = fetch_contract()
    assert "continue-on-error" not in job.split("    steps:", 1)[0]
    assert "continue-on-error" not in step
    assert "$length -gt $maximum" in downloader
    assert "$expected -ge 0 -and $length -ne $expected" in downloader
    assert "$total -gt $maximum" in downloader
    assert "$expected -ge 0 -and $total -ne $expected" in downloader
    assert "$null -ne $length -and $total -ne $length" in downloader
    assert "$buffer = [byte[]]::new(1048576)" in downloader
    assert "Receive-PublicAsset $url $modelPath $asset.lfs.size $asset.lfs.size" in script
    assert "$asset.lfs.size -gt 3000000000" in script
    assert '(Get-FileHash $modelPath -Algorithm SHA256).Hash.ToLowerInvariant()' in script
    assert '$modelSha -cne $asset.lfs.sha256' in script
    assert 'throw "Downloaded conversion does not match its repository LFS SHA-256."' in script
    assert script.index("Receive-PublicAsset $url $modelPath") < script.index("$modelSha =") < script.index('$manifest =')
    acceptance = job.split("      - name: Exercise actual", 1)[1].split("      - name:", 1)[0]
    smoke = job.split("      - name: Require three", 1)[1].split("      - name:", 1)[0]
    assert "continue-on-error" not in acceptance
    assert "continue-on-error" not in smoke
    assert '--request-timeout 600' in acceptance
    assert "foreach ($trial in 1..3)" in smoke
    assert 'throw "Actual governed Node instruction runtime failed' in smoke


TRANSPORT_FIXTURE = r"""
using System;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
public sealed class FixtureHandler : HttpMessageHandler {
    public bool AllowAutoRedirect { get; set; }
    public static string Mode;
    public static int Calls, Disposed, StreamsDisposed;
    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken token) {
        Calls++;
        if (Mode == "http-retry" && Calls == 1)
            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.ServiceUnavailable));
        if (Mode == "http-fatal")
            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.NotFound));
        if ((Mode == "redirect" || Mode == "unsafe-redirect") && Calls == 1 || Mode == "redirect-loop") {
            var redirect = new HttpResponseMessage(HttpStatusCode.Found);
            redirect.Headers.Location = new Uri(Mode == "unsafe-redirect"
                ? "https://huggingface.co.evil.invalid/model"
                : "https://cdn-lfs.hf.co/model");
            return Task.FromResult(redirect);
        }
        var response = new HttpResponseMessage(HttpStatusCode.OK);
        bool stall = Mode == "stall" || Mode == "wall-deadline" || (Mode == "idle-retry" && Calls == 1);
        response.Content = new FixtureContent(stall, Mode == "disconnect-retry" && Calls == 1);
        if (Mode != "undeclared-oversize")
            response.Content.Headers.ContentLength = Mode == "truncated" ? 6 : 5;
        return Task.FromResult(response);
    }
    protected override void Dispose(bool disposing) { if (disposing) Disposed++; base.Dispose(disposing); }
}
public sealed class FixtureContent : HttpContent {
    private readonly FixtureStream stream;
    public FixtureContent(bool stall, bool disconnect) { stream = new FixtureStream(stall, disconnect); }
    protected override bool TryComputeLength(out long length) { length = 0; return false; }
    protected override Task SerializeToStreamAsync(Stream target, TransportContext context) { throw new NotSupportedException(); }
    protected override Task<Stream> CreateContentReadStreamAsync() { return Task.FromResult<Stream>(stream); }
    protected override void Dispose(bool disposing) { if (disposing) stream.Dispose(); base.Dispose(disposing); }
}
public sealed class FixtureStream : MemoryStream {
    private readonly bool stall;
    private readonly bool disconnect;
    public FixtureStream(bool stall, bool disconnect) : base(new byte[] { 1, 2, 3, 4, 5 }) { this.stall = stall; this.disconnect = disconnect; }
    public override bool CanSeek { get { return false; } }
    public override async Task<int> ReadAsync(byte[] buffer, int offset, int count, CancellationToken token) {
        if (stall) await Task.Delay(Timeout.Infinite, token);
        if (disconnect) throw new IOException("fixture connection dropped");
        if (FixtureHandler.Mode == "slow-progress") { await Task.Delay(80, token); count = Math.Min(count, 1); }
        return await base.ReadAsync(buffer, offset, count, token);
    }
    private bool disposed;
    protected override void Dispose(bool disposing) {
        if (disposing && !disposed) { FixtureHandler.StreamsDisposed++; disposed = true; }
        base.Dispose(disposing);
    }
}
"""


RUNTIME_CASES = [
        ("success", 5, 5, True, 1, ""),
        ("slow-progress", 5, 5, True, 1, ""),
        ("http-retry", 5, 5, True, 2, ""),
        ("idle-retry", 5, 5, True, 2, ""),
        ("disconnect-retry", 5, 5, True, 2, ""),
        ("stall", 5, 5, False, 3, "idle timeout"),
        ("wall-deadline", 5, 5, False, 1, "shared 30-minute deadline"),
        ("http-fatal", 5, 5, False, 1, "HTTP 404"),
        ("redirect", 5, 5, True, 2, ""),
        ("unsafe-redirect", 5, 5, False, 1, "approved HTTPS"),
        ("redirect-loop", 5, 5, False, 6, "redirect limit"),
        ("success", 4, 4, False, 1, "declared byte length"),
        ("undeclared-oversize", 4, -1, False, 1, "byte budget"),
        ("truncated", 6, 6, False, 1, "actual byte length"),
        ("initial-http", 5, 5, False, 0, "approved HTTPS"),
        ("initial-port", 5, 5, False, 0, "approved HTTPS"),
        ("initial-userinfo", 5, 5, False, 0, "approved HTTPS"),
]


def assert_extracted_powershell_transport_runtime(tmp_path, mode, maximum, expected, success, calls, reason):
    executable = os.environ.get("PWSH_EXE") or shutil.which("pwsh")
    if not executable:
        raise RuntimeError("PowerShell required for extracted downloader runtime fixtures")
    _, _, script, _ = fetch_contract()
    helper = script.split("$downloadDeadline =", 1)[1].split("\n$url = ", 1)[0]
    helper = "$downloadDeadline =" + helper
    # Replace only the transport and durations in the extracted test copy. The
    # production HTTPS allowlist, retry logic, file I/O and validation are intact.
    helper = helper.replace("[System.Net.Http.HttpClientHandler]::new()", "[FixtureHandler]::new()")
    helper = helper.replace("FromMinutes(30)", "FromSeconds(10)")
    helper = helper.replace("FromSeconds(60)", "FromMilliseconds(150)")
    helper = helper.replace("FromSeconds(5 * $attempt)", "FromMilliseconds(5 * $attempt)")
    if mode == "wall-deadline":
        helper = helper.replace("FromSeconds(10)", "FromMilliseconds(150)")
        helper = helper.replace("$operation.CancelAfter([TimeSpan]::FromMilliseconds(150))",
                                "$operation.CancelAfter([TimeSpan]::FromSeconds(2))")
    url = {
        "initial-http": "http://huggingface.co/model",
        "initial-port": "https://huggingface.co:444/model",
        "initial-userinfo": "https://user:password@huggingface.co/model",
    }.get(mode, "https://huggingface.co/pinned/resolve/revision/model")
    target = tmp_path / "asset"
    fixture = tmp_path / "fixture.ps1"
    fixture.write_text(
        "$ErrorActionPreference = 'Stop'\n"
        "Add-Type -TypeDefinition @'\n" + TRANSPORT_FIXTURE + "\n'@\n"
        f"[FixtureHandler]::Mode = '{mode}'\n" + helper + "\n"
        "$ok = $false; $errorText = ''\n"
        f"try {{ Receive-PublicAsset '{url}' '{target}' {maximum} {expected}; $ok = $true }}\n"
        "catch { $errorText = $_.Exception.Message }\n"
        "$downloadDeadline.Dispose()\n"
        f"@{{ ok = $ok; error = $errorText; calls = [FixtureHandler]::Calls; disposed = [FixtureHandler]::Disposed; streamsDisposed = [FixtureHandler]::StreamsDisposed; exists = (Test-Path -LiteralPath '{target}') }} | ConvertTo-Json -Compress\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [executable, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(fixture)],
        capture_output=True, text=True, timeout=20, check=True,
    )
    receipt = json.loads(result.stdout.strip().splitlines()[-1])
    assert receipt["ok"] is success, result.stdout + result.stderr
    assert receipt["exists"] is success, receipt
    assert receipt["calls"] == calls, receipt
    expected_attempts = min(calls, 3) if mode in ("http-retry", "idle-retry", "disconnect-retry", "stall") else 1
    assert receipt["disposed"] == expected_attempts, receipt
    if mode in ("success", "slow-progress", "idle-retry", "disconnect-retry", "stall", "wall-deadline",
                "undeclared-oversize", "truncated"):
        assert receipt["streamsDisposed"] == expected_attempts, receipt
    if success:
        assert target.read_bytes() == bytes([1, 2, 3, 4, 5])
    else:
        assert reason in receipt["error"], receipt


class DownloadContractTests(unittest.TestCase):
    def test_shared_budget(self):
        assert_one_larger_but_bounded_budget_covers_all_assets_and_retries()

    def test_finite_clean_retries(self):
        assert_transient_retries_are_finite_clean_and_do_not_reuse_signed_urls()

    def test_redirect_security(self):
        assert_every_redirect_is_manually_validated_before_network_access()

    def test_fail_closed_verification(self):
        assert_streaming_sizes_candidate_hash_and_acceptance_still_fail_closed()

    def test_powershell_transport_runtime(self):
        for mode, maximum, expected, success, calls, reason in RUNTIME_CASES:
            with self.subTest(mode=mode, maximum=maximum):
                with tempfile.TemporaryDirectory(prefix=".embedded-model-test-", dir=WORKFLOW.parents[2]) as directory:
                    assert_extracted_powershell_transport_runtime(
                        Path(directory), mode, maximum, expected, success, calls, reason)


if __name__ == "__main__":
    unittest.main()
