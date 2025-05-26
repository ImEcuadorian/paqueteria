import grpc
from concurrent import futures
import json, uuid, datetime
import envio_pb2_grpc, envio_pb2
from pathlib import Path

DATA_FILE = Path('services/envio/envios.json')

class EnvioServicer(envio_pb2_grpc.EnvioServicioServicer):
    def __init__(self):
        try:
            self.db = json.loads(DATA_FILE.read_text())
        except FileNotFoundError:
            self.db = []

    def RegistrarEnvio(self, req, ctx):
        eid = str(uuid.uuid4())
        record = {
            'id_envio': eid,
            'cedula_cliente': req.cedula_cliente,
            'id_paquete': req.id_paquete,
            'fecha': datetime.datetime.utcnow().isoformat()
        }
        self.db.append(record)
        DATA_FILE.write_text(json.dumps(self.db, indent=2))
        return envio_pb2.RegistrarEnvioResponse(id_envio=eid, mensaje='✅ Envío registrado')

    def HistorialEnvios(self, req, ctx):
        found = [e for e in self.db if e['cedula_cliente'] == req.cedula_cliente]
        return envio_pb2.HistorialEnviosResponse(
            envios=[envio_pb2.Envio(**e) for e in found]
        )

def serve():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text('[]')

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    envio_pb2_grpc.add_EnvioServicioServicer_to_server(EnvioServicer(), server)

    with open("../../certs/servidor-envio/server_envio.key", 'rb') as f:
        private_key = f.read()
    with open("../../certs/servidor-envio/server_envio.crt", 'rb') as f:
        certificate_chain = f.read()

    creds = grpc.ssl_server_credentials([(private_key, certificate_chain)])
    server.add_secure_port('[::]:50053', creds)

    server.start()
    print("✅ EnvioService corriendo en el puerto 50053 con TLS")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
