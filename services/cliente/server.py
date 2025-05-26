import grpc
from concurrent import futures
import json
import cliente_pb2_grpc, cliente_pb2
from pathlib import Path

DATA_FILE = Path('services/cliente/clientes.json')

class ClienteServicer(cliente_pb2_grpc.ClienteServicioServicer):
    def __init__(self):
        try:
            self.db = json.loads(DATA_FILE.read_text())
        except FileNotFoundError:
            self.db = {}

    def RegistrarCliente(self, req, ctx):
        self.db[req.cedula] = {
            'nombre': req.nombre,
            'telefono': req.telefono,
            'direccion': req.direccion
        }
        DATA_FILE.write_text(json.dumps(self.db, indent=2))
        return cliente_pb2.RegistrarClienteResponse(mensaje='✅ Cliente registrado')


def serve():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text('{}')

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cliente_pb2_grpc.add_ClienteServicioServicer_to_server(ClienteServicer(), server)

    with open("../../certs/servidor-cliente/server_cliente.key", 'rb') as f:
        private_key = f.read()
    with open("../../certs/servidor-cliente/server_cliente.crt", 'rb') as f:
        certificate_chain = f.read()

    creds = grpc.ssl_server_credentials([(private_key, certificate_chain)])
    server.add_secure_port('[::]:50051', creds)

    server.start()
    print("✅ ClienteService corriendo en el puerto 50051 con TLS")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
