import platform
import psutil
import os



system_info = platform.uname()
print("os cpu count:", os.cpu_count())
#command = 'cat /proc/cpuinfo' 
#print(os.popen(command).read().strip())


print("System Information:")
print(f"System: {system_info.system}")
print(f"Node Name: {system_info.node}")
print(f"Release: {system_info.release}")
print(f"Version: {system_info.version}")
print(f"Machine: {system_info.machine}")
print(f"Processor: {system_info.processor}")


cpu_info = platform.processor()
cpu_count = psutil.cpu_count(logical=False)
logical_cpu_count = psutil.cpu_count(logical=True)

print("\nCPU Information:")
print(f"Processor: {cpu_info}")
print(f"Physical Cores: {cpu_count}")
print(f"Logical Cores: {logical_cpu_count}")

memory_info = psutil.virtual_memory()

print("\nMemory Information:")
print(f"Total Memory: {memory_info.total} bytes")
print(f"Available Memory: {memory_info.available} bytes")
print(f"Used Memory: {memory_info.used} bytes")
print(f"Memory Utilization: {memory_info.percent}%")

disk_info = psutil.disk_usage('/')

print("\nDisk Information:")
print(f"Total Disk Space: {disk_info.total} bytes")
print(f"Used Disk Space: {disk_info.used} bytes")
print(f"Free Disk Space: {disk_info.free} bytes")
print(f"Disk Space Utilization: {disk_info.percent}%")

