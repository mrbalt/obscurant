"""Runs a program on Windows with reduced rights: no privileges, low integrity level, inside a job
object that kills it with the helper, allows no child processes and caps its memory. It is NOT cut
off from the network (that needs an AppContainer); the Linux version is."""
import ctypes
import ctypes.wintypes as wt
import os
import threading

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
adv = ctypes.WinDLL("advapi32", use_last_error=True)

H, P, D, B = wt.HANDLE, ctypes.c_void_p, wt.DWORD, wt.BOOL


def _sig(fn, res, *args):
    fn.restype = res
    fn.argtypes = list(args)


_sig(k32.GetCurrentProcess, H)
_sig(k32.CloseHandle, B, H)
_sig(k32.CreatePipe, B, P, P, P, D)
_sig(k32.SetHandleInformation, B, H, D, D)
_sig(k32.ReadFile, B, H, P, D, P, P)
_sig(k32.WriteFile, B, H, P, D, P, P)
_sig(k32.CreateJobObjectW, H, P, wt.LPCWSTR)
_sig(k32.SetInformationJobObject, B, H, ctypes.c_int, P, D)
_sig(k32.AssignProcessToJobObject, B, H, H)
_sig(k32.TerminateJobObject, B, H, ctypes.c_uint)
_sig(k32.ResumeThread, D, H)
_sig(k32.WaitForSingleObject, D, H, D)
_sig(k32.GetExitCodeProcess, B, H, P)
_sig(k32.CreateFileW, H, wt.LPCWSTR, D, D, P, D, D, H)
_sig(adv.OpenProcessToken, B, H, D, P)
_sig(adv.CreateRestrictedToken, B, H, D, D, P, D, P, D, P, P)
_sig(adv.ConvertStringSidToSidW, B, wt.LPCWSTR, P)
_sig(adv.SetTokenInformation, B, H, ctypes.c_int, P, D)
_sig(adv.CreateProcessAsUserW, B, H, wt.LPCWSTR, wt.LPWSTR, P, P, B, D, P, wt.LPCWSTR, P, P)

DISABLE_MAX_PRIVILEGE = 0x1
LUA_TOKEN = 0x4
TOKEN_ALL_NEEDED = 0x0002 | 0x0001 | 0x0008 | 0x0080 | 0x0020
TokenIntegrityLevel = 25
SE_GROUP_INTEGRITY = 0x20
CREATE_SUSPENDED = 0x4
CREATE_NO_WINDOW = 0x08000000
STARTF_USESTDHANDLES = 0x100
HANDLE_FLAG_INHERIT = 1
JobObjectExtendedLimitInformation = 9
JobObjectBasicUIRestrictions = 4
JOB_LIMITS = 0x2000 | 0x8 | 0x100  # kill on close, active process limit, process memory
MEMORY_CAP = 3 << 30


class SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Sid", ctypes.c_void_p), ("Attributes", wt.DWORD)]


class STARTUPINFOW(ctypes.Structure):
    _fields_ = [("cb", wt.DWORD), ("lpReserved", wt.LPWSTR), ("lpDesktop", wt.LPWSTR), ("lpTitle", wt.LPWSTR),
                ("dwX", wt.DWORD), ("dwY", wt.DWORD), ("dwXSize", wt.DWORD), ("dwYSize", wt.DWORD),
                ("dwXCountChars", wt.DWORD), ("dwYCountChars", wt.DWORD), ("dwFillAttribute", wt.DWORD),
                ("dwFlags", wt.DWORD), ("wShowWindow", wt.WORD), ("cbReserved2", wt.WORD),
                ("lpReserved2", ctypes.c_void_p), ("hStdInput", wt.HANDLE), ("hStdOutput", wt.HANDLE),
                ("hStdError", wt.HANDLE)]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [("hProcess", wt.HANDLE), ("hThread", wt.HANDLE), ("dwProcessId", wt.DWORD), ("dwThreadId", wt.DWORD)]


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [(n, ctypes.c_ulonglong) for n in ("a", "b", "c", "d", "e", "f")]


class BASIC_LIMITS(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", wt.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wt.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", wt.DWORD), ("SchedulingClass", wt.DWORD)]


class EXTENDED_LIMITS(ctypes.Structure):
    _fields_ = [("Basic", BASIC_LIMITS), ("Io", IO_COUNTERS), ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t)]


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("nLength", wt.DWORD), ("lpSecurityDescriptor", ctypes.c_void_p), ("bInheritHandle", wt.BOOL)]


def _check(ok, what):
    if not ok:
        raise OSError(f"{what} failed ({ctypes.get_last_error()})")


def _pipe(read_inheritable):
    sa = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), None, True)
    r, w = wt.HANDLE(), wt.HANDLE()
    _check(k32.CreatePipe(ctypes.byref(r), ctypes.byref(w), ctypes.byref(sa), 0), "CreatePipe")
    ours = w if read_inheritable else r
    _check(k32.SetHandleInformation(ours, HANDLE_FLAG_INHERIT, 0), "SetHandleInformation")
    return r, w


def _read_all(handle):
    chunks = []
    buf = ctypes.create_string_buffer(65536)
    got = wt.DWORD()
    while k32.ReadFile(handle, buf, len(buf), ctypes.byref(got), None) and got.value:
        chunks.append(buf.raw[:got.value])
    return b"".join(chunks)


def _restricted_token():
    cur = wt.HANDLE()
    _check(adv.OpenProcessToken(k32.GetCurrentProcess(), TOKEN_ALL_NEEDED, ctypes.byref(cur)), "OpenProcessToken")
    new = wt.HANDLE()
    _check(adv.CreateRestrictedToken(cur, DISABLE_MAX_PRIVILEGE | LUA_TOKEN, 0, None, 0, None, 0, None,
                                     ctypes.byref(new)), "CreateRestrictedToken")
    sid = ctypes.c_void_p()
    _check(adv.ConvertStringSidToSidW("S-1-16-4096", ctypes.byref(sid)), "ConvertStringSidToSid")
    label = SID_AND_ATTRIBUTES(sid, SE_GROUP_INTEGRITY)
    _check(adv.SetTokenInformation(new, TokenIntegrityLevel, ctypes.byref(label),
                                   ctypes.sizeof(label) + 16), "SetTokenInformation")
    k32.CloseHandle(cur)
    return new


def _job():
    job = k32.CreateJobObjectW(None, None)
    _check(job, "CreateJobObject")
    ext = EXTENDED_LIMITS()
    ext.Basic.LimitFlags = JOB_LIMITS
    ext.Basic.ActiveProcessLimit = 1
    ext.ProcessMemoryLimit = MEMORY_CAP
    _check(k32.SetInformationJobObject(job, JobObjectExtendedLimitInformation, ctypes.byref(ext),
                                       ctypes.sizeof(ext)), "SetInformationJobObject")
    ui = wt.DWORD(0xFF)
    k32.SetInformationJobObject(job, JobObjectBasicUIRestrictions, ctypes.byref(ui), ctypes.sizeof(ui))
    return job


def run(argv, stdin_data, timeout=40):
    """Returns (exit_code, stdout_bytes)."""
    token = _restricted_token()
    job = _job()
    in_r, in_w = _pipe(read_inheritable=True)
    out_r, out_w = _pipe(read_inheritable=False)
    null = k32.CreateFileW("NUL", 0x40000000, 3, None, 3, 0, None)
    si = STARTUPINFOW()
    si.cb = ctypes.sizeof(si)
    si.dwFlags = STARTF_USESTDHANDLES
    si.hStdInput, si.hStdOutput, si.hStdError = in_r, out_w, null
    sa = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), None, True)
    k32.SetHandleInformation(null, HANDLE_FLAG_INHERIT, HANDLE_FLAG_INHERIT)
    pi = PROCESS_INFORMATION()
    cmd = ctypes.create_unicode_buffer(" ".join(f'"{a}"' if (" " in a or not a) else a for a in argv))
    ok = adv.CreateProcessAsUserW(token, argv[0], cmd, None, None, True, CREATE_SUSPENDED | CREATE_NO_WINDOW,
                                  None, os.path.dirname(argv[0]) or None, ctypes.byref(si), ctypes.byref(pi))
    _check(ok, "CreateProcessAsUser")
    _check(k32.AssignProcessToJobObject(job, pi.hProcess), "AssignProcessToJobObject")
    k32.ResumeThread(pi.hThread)
    for h in (in_r, out_w, null):
        k32.CloseHandle(h)

    def feed():
        written = wt.DWORD()
        view = memoryview(stdin_data)
        pos = 0
        while pos < len(view):
            chunk = bytes(view[pos:pos + 65536])
            if not k32.WriteFile(in_w, chunk, len(chunk), ctypes.byref(written), None):
                break
            pos += written.value
        k32.CloseHandle(in_w)

    threading.Thread(target=feed, daemon=True).start()
    result = []
    reader = threading.Thread(target=lambda: result.append(_read_all(out_r)), daemon=True)
    reader.start()
    waited = k32.WaitForSingleObject(pi.hProcess, int(timeout * 1000))
    if waited != 0:
        k32.TerminateJobObject(job, 1)
    code = wt.DWORD()
    k32.GetExitCodeProcess(pi.hProcess, ctypes.byref(code))
    reader.join(2)
    for h in (pi.hProcess, pi.hThread, out_r, job, token):
        k32.CloseHandle(h)
    return code.value, (result[0] if result else b"")
