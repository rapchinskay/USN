import ctypes
from ctypes import wintypes
import os

# конст
MAX_PATH = 260
FILE_SUPPORTS_USN_JOURNAL = 0x02000000
FSCTL_READ_FILE_USN_DATA = 0x000900eb
USN_SIZE = 4096

def check(file_path):
    file_system_flags = wintypes.DWORD()
    ctypes.windll.kernel32.GetVolumeInformationW(ctypes.c_wchar_p(file_path), None, 0, None, None, ctypes.byref(file_system_flags), None, 0)
    if file_system_flags.value & FILE_SUPPORTS_USN_JOURNAL:
        print("Файловая система ПОДДЕРЖИВАЕТ журнал USN")
    else:
        print("Файловая система НЕ поддерживает журнал USN")

class USN_RECORD_V2(ctypes.Structure):
    _fields_ = [
        ("RecordLength", wintypes.DWORD),
        ("MajorVersion", wintypes.WORD),
        ("MinorVersion", wintypes.WORD),
        ("FileReferenceNumber", wintypes.LARGE_INTEGER),
        ("ParentFileReferenceNumber", wintypes.LARGE_INTEGER),
        ("Usn", wintypes.LARGE_INTEGER),
        #+8
    ]

class USN_RECORD_V3(ctypes.Structure):
    _fields_ = [
        ("RecordLength", wintypes.DWORD),
        ("MajorVersion", wintypes.WORD),
        ("MinorVersion", wintypes.WORD),
        ("FileReferenceNumber", wintypes.LARGE_INTEGER),
        ("ParentFileReferenceNumber", wintypes.LARGE_INTEGER),
        ("Usn", wintypes.LARGE_INTEGER),
        #+8+2
    ]

def handle(file_path):
    return ctypes.windll.kernel32.CreateFileW(file_path, 0x80000000, 0x00000001 | 0x00000002, None, 3, 0, None)

def usn_id(file_path):
    file_handle = handle(file_path)
    usn_buf = ctypes.create_string_buffer(USN_SIZE)
    urv2 = USN_RECORD_V2.from_buffer(usn_buf)
    urv3 = USN_RECORD_V3.from_buffer(usn_buf)
    uLength = wintypes.DWORD()
    ctypes.windll.kernel32.DeviceIoControl(file_handle, FSCTL_READ_FILE_USN_DATA , None, 0, usn_buf, USN_SIZE, ctypes.byref(uLength), None)

    if urv2.MajorVersion == 2:
        return urv2.Usn,2.0
    else:
        return urv3.Usn,3.0

print("формат: 'D:\\filefile'")
disk_path = input("путь к диску: ")
check(disk_path[:3])

for root, dirs, files in os.walk(disk_path):
    for file_name in files:
        try:
            file_path = os.path.join(root, file_name)
            usn_number, version = usn_id(file_path)
            print(f"Путь: {file_path}")
            print(f"USN ID: 0x{hex(usn_number)[2:]}, Версия Журнала: {version}")
            print("-" * 50)
        except:
            continue
