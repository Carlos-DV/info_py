import platform,socket,re,uuid,json,psutil, os, wmi,subprocess, winreg, win32com, sys, struct,cpuinfo

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor



so =  platform.system() + " " + platform.release()
soVersion = platform.version()
windowsType = platform.win32_edition()
architecture = platform.machine()
hostname = socket.gethostname()
ipaddress = socket.gethostbyname(socket.gethostname())
macaddress = ":".join(re.findall('..',"%012x" % uuid.getnode()))
cpu = cpuinfo.get_cpu_info()['brand_raw']
pFisicos = psutil.cpu_count(logical=False)
pLogicos = psutil.cpu_count(logical=True)
ram = round(psutil.virtual_memory().total/(1024**3))


system_info = {
    "sistema_operativo": so,
    "version_sistema_operativo": soVersion,
    "tipo_windows": windowsType,
    "arquitectura": architecture,
    "nombre_host": hostname,
    "direccion_ip": ipaddress,
    "direccion_mac": macaddress,
    "procesador": cpu,
    "procesadores_fisicos": pFisicos,
    "procesadores_logicos": pLogicos,
    "ram": ram,
    "particiones": [],
    "monitor": [],
}

partitions = psutil.disk_partitions()

# Iterar sobre cada partición de disco y obtener su información
for partition in partitions:
    letterDisk = partition.device
    fileSystem = partition.fstype
    try:
        partition_usage = psutil.disk_usage(partition.mountpoint)
    except PermissionError:
        continue

    # Crear un diccionario con la información de la partición
    partition_info = {
        "letra_disco": letterDisk,
        "sistema_archivos": fileSystem,
        "tamano_total": get_size(partition_usage.total),
        "tamano_usado": get_size(partition_usage.used),
        "porcentaje_usado": partition_usage.percent
    }

    # Agregar el diccionario de la partición al diccionario del sistema
    system_info["particiones"].append(partition_info)
#monitors
def get_monitor_info():
    wmi_obj = wmi.WMI(namespace="root\\wmi")
    monitor_info = wmi_obj.query("SELECT * FROM WmiMonitorID")
    monitors = []
    if not monitor_info:
        return None # No monitor detected
    for monitor in monitor_info:
        # Get the monitor serial number
        serial = ''.join([chr(char) for char in monitor.SerialNumberID]).rstrip('\0')
        # Get the monitor manufacturer and model
        manufacturer = ''.join([chr(char) for char in monitor.ManufacturerName]).rstrip('\0')
        product = ''.join([chr(char) for char in monitor.UserFriendlyName]).rstrip('\0')
        monitors.append({"Serial": serial, "Manufacturer": manufacturer, "Model": product})
    return monitors

if __name__ == "__main__":
    monitors = get_monitor_info()
    if not monitors:
        print("No monitor detected.")
    else:
        system_info["monitor"].append(monitors)


# Convertir el diccionario del sistema a una cadena JSON
system_info_json = json.dumps(system_info, indent=4)

# Guardar la cadena JSON en un archivo
with open("C:/projects/info_sistema.json", "w") as f:
    f.write(system_info_json)