import os
import sys
import asyncio
import grpc
from grpc_reflection.v1alpha import reflection

try:
    from app.generated import glossary_pb2 as pb
    from app.generated import glossary_pb2_grpc as rpc
except Exception:
    CURRENT_DIR = os.path.dirname(__file__)
    GENERATED_DIR = os.path.join(CURRENT_DIR, "generated")
    if GENERATED_DIR not in sys.path:
        sys.path.append(GENERATED_DIR)
    import glossary_pb2 as pb
    import glossary_pb2_grpc as rpc

from app.db import init_db, get_term, list_terms, add_term

GRPC_PORT = int(os.getenv("GRPC_PORT", "50051"))

class GlossarySrv(rpc.GlossaryServiceServicer):
    async def GetTerm(self, request, context):
        data = await get_term(request.keyword)
        if not data:
            await context.abort(grpc.StatusCode.NOT_FOUND, "Term not found")
        return pb.GetTermResponse(term=pb.Term(**data))

    async def ListTerms(self, request, context):
        items, total = await list_terms(request.limit or 10, request.offset or 0)
        return pb.ListTermsResponse(
            terms=[pb.Term(**i) for i in items],
            total=total
        )

    async def AddTerm(self, request, context):
        term = {"keyword": request.term.keyword,
                "title": request.term.title,
                "description": request.term.description}
        ok = await add_term(term)
        return pb.AddTermResponse(success=ok)

async def serve():
    await init_db()
    server = grpc.aio.server()
    rpc.add_GlossaryServiceServicer_to_server(GlossarySrv(), server)

    service_names = (
        pb.DESCRIPTOR.services_by_name['GlossaryService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)

    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    await server.start()
    print(f"Glossary gRPC server started on port {GRPC_PORT}")
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
