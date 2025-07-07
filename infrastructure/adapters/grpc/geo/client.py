from grpclib.client import Channel

from core.domain.shared_kernel.location import Location
from core.ports.geo_service_interface import GeoServiceInterface
from infrastructure.adapters.grpc.geo import Contract_pb2
from infrastructure.adapters.grpc.geo.Contract_grpc import GeoStub


class GRPCGeoService(GeoServiceInterface):
    def __init__(self, host: str = "localhost", port: int = 5004):
        self._host = host
        self._port = port

    async def get_location(self, street: str) -> Location:
        async with Channel(self._host, self._port) as channel:
            stub = GeoStub(channel)
            request = Contract_pb2.GetGeolocationRequest(Street=street)
            response = await stub.GetGeolocation(request)
            loc = response.Location
            return Location(x=loc.x, y=loc.y)
