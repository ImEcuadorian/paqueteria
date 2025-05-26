
import grpc
import cliente_pb2, cliente_pb2_grpc

def main():
    with open("../../certs/servidor-cliente/server_cliente.crt", "rb") as f:
        trusted_certs = f.read()
    creds = grpc.ssl_channel_credentials(root_certificates=trusted_certs)

    channel = grpc.secure_channel("localhost:50051", creds)
    stub = cliente_pb2_grpc.ClienteServicioStub(channel)

    request = cliente_pb2.RegistrarClienteRequest(
        nombre="Mauricio",
        cedula="0102030405",
        telefono="0999999999",
        direccion="Av. Universitaria 123, Quito"
    )
    response = stub.RegistrarCliente(request)
    print(response.mensaje)

if __name__ == "__main__":
    main()
