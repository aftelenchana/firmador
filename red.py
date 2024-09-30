from scapy.all import *

# Nombre del archivo donde se guardarán los paquetes capturados
output_file = "paquetes_capturados.txt"

# Función de callback que se llama por cada paquete capturado
def packet_callback(packet):
    # Verificar si el paquete contiene capas de datos superiores (como HTTP)
    if packet.haslayer(TCP) and packet.haslayer(Raw):
        # Obtener y guardar el contenido de la capa de datos (por ejemplo, HTTP)
        raw_data = packet[Raw].load
        try:
            decoded_data = raw_data.decode('utf-8', errors='ignore')
            with open(output_file, "a", encoding="utf-8") as file:
                file.write(f"Paquete capturado:\n{decoded_data}\n\n")
            # Imprimir también en la consola (opcional)
            print(f"Paquete capturado:\n{decoded_data}\n")
        except UnicodeDecodeError:
            # Si no se puede decodificar como UTF-8, guardar como binario
            with open(output_file, "a", encoding="utf-8") as file:
                file.write(f"Paquete capturado (contenido binario):\n{raw_data.hex()}\n\n")
            # Imprimir también en la consola (opcional)
            print(f"Paquete capturado (contenido binario):\n{raw_data.hex()}\n")

# Especificar la interfaz de red
interface = "Wi-Fi 2"

# Capturar paquetes
print(f"Capturando tráfico en la interfaz {interface} y guardando en {output_file}...")
sniff(iface=interface, prn=packet_callback, store=0)
