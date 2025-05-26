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

    def login(self, req, ctx):
        if req.cedula in self.db:
            return cliente_pb2.LoginResponse(
                mensaje='✅ Login exitoso',
            )
        else:
            ctx.set_code(grpc.StatusCode.NOT_FOUND)
            ctx.set_details('Cliente no encontrado')
            return cliente_pb2.LoginResponse()

    def actualizarCliente(self, req, ctx):
        if req.cedula in self.db:
            self.db[req.cedula].update({
                'nombre': req.nombre,
                'telefono': req.telefono,
                'direccion': req.direccion
            })
            DATA_FILE.write_text(json.dumps(self.db, indent=2))
            return cliente_pb2.ActualizarClienteResponse(mensaje='✅ Cliente actualizado')
        else:
            ctx.set_code(grpc.StatusCode.NOT_FOUND)
            ctx.set_details('Cliente no encontrado')
            return cliente_pb2.ActualizarClienteResponse()

    def eliminarCliente(self, req, ctx):
        if req.cedula in self.db:
            del self.db[req.cedula]
            DATA_FILE.write_text(json.dumps(self.db, indent=2))
            return cliente_pb2.EliminarClienteResponse(mensaje='✅ Cliente eliminado')
        else:
            ctx.set_code(grpc.StatusCode.NOT_FOUND)
            ctx.set_details('Cliente no encontrado')
            return cliente_pb2.EliminarClienteResponse()

    def buscarClientePorCedula(self, req, ctx):
        if req.cedula in self.db:
            cliente_data = self.db[req.cedula]
            return cliente_pb2.ObtenerClienteResponse(
                cedula=req.cedula,
                nombre=cliente_data['nombre'],
                telefono=cliente_data['telefono'],
                direccion=cliente_data['direccion']
            )
        else:
            ctx.set_code(grpc.StatusCode.NOT_FOUND)
            ctx.set_details('Cliente no encontrado')
            return cliente_pb2.ObtenerClienteResponse()

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
