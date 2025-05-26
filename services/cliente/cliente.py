
import grpc
import cliente_pb2, cliente_pb2_grpc
from services.envio import envio_pb2_grpc
from services.paquete import paquete_pb2_grpc


def main():
    with open("../../certs/servidor-cliente/server_cliente.crt", "rb") as f:
        trusted_certs = f.read()
    creds = grpc.ssl_channel_credentials(root_certificates=trusted_certs)

    with open("../../certs/servidor-paquete/server_paquete.crt", "rb") as f:
        trusted_certs_paquete = f.read()

    creds_1 = grpc.ssl_channel_credentials(root_certificates=trusted_certs_paquete)

    with open("../../certs/servidor-envio/server_envio.crt", "rb") as f:
        trusted_certs_envio = f.read()

    creds_2 = grpc.ssl_channel_credentials(root_certificates=trusted_certs_envio)


    channel = grpc.secure_channel("localhost:50051", creds)
    channel_1 = grpc.secure_channel("localhost:50052", creds_1)
    channel_2 = grpc.secure_channel("localhost:50053", creds_2)
    stub = cliente_pb2_grpc.ClienteServicioStub(channel)
    stub_1 = envio_pb2_grpc.EnvioServicioStub(channel_1)
    stub_2 = paquete_pb2_grpc.PaqueteServicioStub(channel_2)

    request = cliente_pb2.RegistrarClienteRequest(
        nombre="Mauricio",
        cedula="0102030405",
        telefono="0999999999",
        direccion="Av. Universitaria 123, Quito"
    )
    response = stub.RegistrarCliente(request)
    print(response.mensaje)

    request = cliente_pb2.ActualizarClienteRequest(
        cedula="0102030405",
        nombre="Mauricio Perez",
        telefono="0998888888",
        direccion="Av. Universitaria 456, Quito"
    )
    response = stub.ActualizarCliente(request)
    print(response.mensaje)

    request = cliente_pb2.EliminarClienteRequest(cedula="0102030405")
    response = stub.EliminarCliente(request)
    print(response.mensaje)

    request1 =  stub_2.RegistrarPaqueteRequest(
        peso=2.5,
        dimensiones="30x20x10",
        destino="Quito"
    )
    response1 = stub_2.RegistrarPaquete(request1)
    print(response1.mensaje)

    request_10 = stub_1.RegistrarEnvioRequest(
        cedula_cliente="0102030405",
        id_paquete=response1.id
    )
    response_10 = stub_1.RegistrarEnvio(request_10)
    print(response_10.mensaje)

    request2 = stub_2.ActualizarEstadoRequest(
        id=response1.id,
        estado="En Espera"
    )

    response2 = stub_2.ActualizarEstado(request2)
    print(response2.mensaje)

    request3 = stub_2.ListarPaquetesRequest()
    response3 = stub_2.ListarPaquetes(request3)

    print("Paquetes registrados:")
    for paquete in response3.paquetes:
        print(f"ID: {paquete.id}, Peso: {paquete.peso}, Dimensiones: {paquete.dimensiones}, Destino: {paquete.destino}, Estado: {paquete.estado}")

    request4 = stub_2.EliminarPaqueteRequest(id=response1.id)
    response4 = stub_2.EliminarPaquete(request4)
    print(response4.mensaje)

if __name__ == "__main__":
    main()
