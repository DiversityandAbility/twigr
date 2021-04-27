import io
from typing import Callable, List

from fastapi import Body, APIRouter, BackgroundTasks
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response
from syslog_rfc5424_parser import SyslogMessage

from app import db


class SyslogRequest(Request):
    async def json(self) -> List[dict]:
        if not hasattr(self, "_json"):
            self._json = []
            async for line in self.read_lines():
                print("line=", line)
                line = line.decode("utf-8")
                msg = SyslogMessage.parse(line)
                self._json.append(msg.as_dict())
        return self._json

    async def read_lines(self):
        body = await self.body()
        print("body=", body)
        stream = io.BytesIO(body)
        done = False
        while not done:
            frame_size = self.get_frame_size(stream)
            print("framesize=", frame_size)
            if frame_size is None:
                done = True
            else:
                yield stream.read(frame_size)

    def get_frame_size(self, stream):
        """This function was inspired by
        https://github.com/stephane-martin/pyloggr/blob/8715300a091a1423639fe259456e6fc6c982724e/pyloggr/utils/__init__.py#L269
        """
        token = io.BytesIO()
        while True:
            c = stream.read(1)
            print("c=", c)
            if not c:
                break
            if c == b" ":
                v = token.getvalue()
                if v:
                    token.close()
                    return int(v)
            else:
                token.write(c)


class SyslogRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = SyslogRequest(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler


router = APIRouter(route_class=SyslogRoute)


@router.post("/", response_class=Response, status_code=201)
async def create_twig(
    background: BackgroundTasks, message: List[dict] = Body(...)
):
    background.add_task(save_twig, message)
    return None


async def save_twig(message: List[dict]):
    for m in message:
        await db.create_twig({"project": None, "data": m})
