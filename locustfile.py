"""
Locust нагрузочное тестирование для gRPC Glossary Service
"""
import grpc
import time
import random
from locust import User, task, between, events
from locust.exception import LocustError

try:
    from app.generated import glossary_pb2 as pb
    from app.generated import glossary_pb2_grpc as rpc
except ImportError:
    import sys
    import os
    generated_path = os.path.join(os.path.dirname(__file__), 'app', 'generated')
    sys.path.insert(0, generated_path)
    import glossary_pb2 as pb
    import glossary_pb2_grpc as rpc


class GrpcClient:
    """gRPC клиент для взаимодействия с GlossaryService"""

    def __init__(self, host: str):
        self.host = host
        self._channel = None
        self._stub = None

    def connect(self):
        """Установить соединение с gRPC сервером"""
        self._channel = grpc.insecure_channel(self.host)
        self._stub = rpc.GlossaryServiceStub(self._channel)

    def close(self):
        """Закрыть соединение"""
        if self._channel:
            self._channel.close()

    def get_term(self, keyword: str):
        """Получить термин по ключевому слову"""
        request = pb.GetTermRequest(keyword=keyword)
        return self._stub.GetTerm(request)

    def list_terms(self, limit: int = 10, offset: int = 0):
        """Получить список терминов"""
        request = pb.ListTermsRequest(limit=limit, offset=offset)
        return self._stub.ListTerms(request)

    def add_term(self, keyword: str, title: str, description: str):
        """Добавить новый термин"""
        term = pb.Term(keyword=keyword, title=title, description=description)
        request = pb.AddTermRequest(term=term)
        return self._stub.AddTerm(request)


class GrpcUser(User):
    """Locust пользователь для gRPC тестирования"""

    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = GrpcClient(self.host)
        self.client.connect()

    def on_stop(self):
        """Вызывается при остановке пользователя"""
        self.client.close()


class GlossaryUser(GrpcUser):
    """Симуляция пользователя работающего с глоссарием"""

    wait_time = between(1, 3)

    # Список известных терминов для тестирования
    KNOWN_KEYWORDS = ["ast", "gof", "observer", "grpc", "protobuf"]

    # Счетчик для генерации уникальных терминов
    term_counter = 0

    @task(5)
    def get_term(self):
        """Получить существующий термин (вес 5)"""
        keyword = random.choice(self.KNOWN_KEYWORDS)
        start_time = time.time()

        try:
            response = self.client.get_term(keyword)
            total_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type="grpc",
                name="GetTerm",
                response_time=total_time,
                response_length=len(response.term.description) if response.term else 0,
                exception=None,
                context={}
            )
        except grpc.RpcError as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(
                request_type="grpc",
                name="GetTerm",
                response_time=total_time,
                response_length=0,
                exception=e,
                context={}
            )

    @task(3)
    def list_terms(self):
        """Получить список терминов (вес 3)"""
        limit = random.choice([5, 10, 20])
        offset = random.choice([0, 5, 10])
        start_time = time.time()

        try:
            response = self.client.list_terms(limit=limit, offset=offset)
            total_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type="grpc",
                name="ListTerms",
                response_time=total_time,
                response_length=len(response.terms),
                exception=None,
                context={}
            )
        except grpc.RpcError as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(
                request_type="grpc",
                name="ListTerms",
                response_time=total_time,
                response_length=0,
                exception=e,
                context={}
            )

    @task(1)
    def add_term(self):
        """Добавить новый термин (вес 1)"""
        GlossaryUser.term_counter += 1
        keyword = f"test_term_{GlossaryUser.term_counter}_{int(time.time())}"
        title = f"Test Term {GlossaryUser.term_counter}"
        description = f"Description for test term {GlossaryUser.term_counter}"

        start_time = time.time()

        try:
            response = self.client.add_term(keyword, title, description)
            total_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type="grpc",
                name="AddTerm",
                response_time=total_time,
                response_length=1 if response.success else 0,
                exception=None,
                context={}
            )
        except grpc.RpcError as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(
                request_type="grpc",
                name="AddTerm",
                response_time=total_time,
                response_length=0,
                exception=e,
                context={}
            )

    @task(2)
    def get_nonexistent_term(self):
        """Попытаться получить несуществующий термин (тест обработки ошибок, вес 2)"""
        keyword = f"nonexistent_{random.randint(1, 10000)}"
        start_time = time.time()

        try:
            response = self.client.get_term(keyword)
            total_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type="grpc",
                name="GetTerm (Not Found)",
                response_time=total_time,
                response_length=0,
                exception=None,
                context={}
            )
        except grpc.RpcError as e:
            total_time = int((time.time() - start_time) * 1000)
            # NOT_FOUND ошибка ожидается, поэтому не считаем это failure
            if e.code() == grpc.StatusCode.NOT_FOUND:
                events.request.fire(
                    request_type="grpc",
                    name="GetTerm (Not Found)",
                    response_time=total_time,
                    response_length=0,
                    exception=None,
                    context={}
                )
            else:
                events.request.fire(
                    request_type="grpc",
                    name="GetTerm (Not Found)",
                    response_time=total_time,
                    response_length=0,
                    exception=e,
                    context={}
                )


class ReadOnlyUser(GrpcUser):
    """Пользователь, который только читает данные (без записи)"""

    wait_time = between(0.5, 2)

    KNOWN_KEYWORDS = ["ast", "gof", "observer", "grpc", "protobuf"]

    @task(7)
    def get_term(self):
        """Получить термин"""
        keyword = random.choice(self.KNOWN_KEYWORDS)
        start_time = time.time()

        try:
            response = self.client.get_term(keyword)
            total_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type="grpc",
                name="[RO] GetTerm",
                response_time=total_time,
                response_length=len(response.term.description) if response.term else 0,
                exception=None,
                context={}
            )
        except grpc.RpcError as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(
                request_type="grpc",
                name="[RO] GetTerm",
                response_time=total_time,
                response_length=0,
                exception=e,
                context={}
            )

    @task(3)
    def list_terms(self):
        """Получить список терминов"""
        limit = random.choice([10, 20, 50])
        start_time = time.time()

        try:
            response = self.client.list_terms(limit=limit, offset=0)
            total_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type="grpc",
                name="[RO] ListTerms",
                response_time=total_time,
                response_length=len(response.terms),
                exception=None,
                context={}
            )
        except grpc.RpcError as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(
                request_type="grpc",
                name="[RO] ListTerms",
                response_time=total_time,
                response_length=0,
                exception=e,
                context={}
            )
