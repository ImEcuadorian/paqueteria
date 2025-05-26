import grpc
from concurrent import futures
import json, uuid
import paquete_pb2_grpc, paquete_pb2
from pathlib import Path

DATA_FILE = Path('services/paquete/paquetes.json')

class PaqueteServicer(paquete_pb2_grpc.PaqueteServicioServicer):
    def __init__(self):
        try:
            self.db = json.loads(DATA_FILE.read_text())
        except FileNotFoundError:
            self.db = {}

    def RegistrarPaquete(self, req, ctx):
        pid = str(uuid.uuid4())
        self.db[pid] = {
            'peso': req.peso,
            'dimensiones': req.dimensiones,
            'destino': req.destino,
            'estado': 'En Espera'
        }
        DATA_FILE.write_text(json.dumps(self.db, indent=2))
        return paquete_pb2.RegistrarPaqueteResponse(id=pid, mensaje='✅ Paquete registrado')

def serve():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text('{}')

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    paquete_pb2_grpc.add_PaqueteServicioServicer_to_server(PaqueteServicer(), server)

    with open("../../certs/servidor-paquete/server_paquete.key", 'rb') as f:
        private_key = f.read()
    with open("../../certs/servidor-paquete/server_paquete.crt", 'rb') as f:
        certificate_chain = f.read()

    creds = grpc.ssl_server_credentials([(private_key, certificate_chain)])
    server.add_secure_port('[::]:50052', creds)

    server.start()
    print("✅ PaqueteService corriendo en el puerto 50052 con TLS")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
