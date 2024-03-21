"""Bluesky adaptive agent for the MVP full stack demo.
This will work from `bluesky-pods`, consume simulated detector data, provide random feedback to the simulated
beamline, and produce documents for Tiled consumption. 
This is primarily for testing and building UI. 
"""

from typing import Dict, Sequence, Tuple, Union

import numpy as np
import tiled.client.node  # noqa: F401
from bluesky_adaptive.agents.base import Agent as BaseAgent
from bluesky_adaptive.agents.base import AgentConsumer
from bluesky_adaptive.server import register_variable, shutdown_decorator, startup_decorator
from bluesky_kafka import Publisher
from bluesky_queueserver_api.zmq import REManagerAPI
from numpy.typing import ArrayLike
from tiled.client import from_profile


class MVPFullStackAgent(BaseAgent):
    def __init__(
        self,
        motor_name="motor",
        detector_name="noisy_det",
        kafka_bootstrap_servers="kafka:29092",
        pub_topic="mad.agent.documents",
        kafka_producer_config=None,
        tiled_profile="testing_sandbox",
    ):
        qs = REManagerAPI(zmq_control_addr="tcp://queue_manager:60615", zmq_info_addr="tcp://queue_manager:60625")

        kafka_consumer = AgentConsumer(
            topics=["mad.bluesky.documents"],
            bootstrap_servers=kafka_bootstrap_servers,
            group_id="test.communication.group",
            consumer_config={"auto.offset.reset": "latest"},
        )
        kafka_producer_config = kafka_producer_config = {
            "acks": 1,
            "enable.idempotence": False,
            "request.timeout.ms": 1000,
            "bootstrap.servers": "kafka:9092",
        } or kafka_producer_config
        kafka_producer = Publisher(
            topic=pub_topic,
            bootstrap_servers=kafka_bootstrap_servers,
            key="",
            producer_config=kafka_producer_config,
        )
        tiled_data_node = from_profile(tiled_profile)
        tiled_agent_node = from_profile(tiled_profile)

        super().__init__(
            kafka_consumer=kafka_consumer,
            kafka_producer=kafka_producer,
            tiled_agent_node=tiled_agent_node,
            tiled_data_node=tiled_data_node,
            qserver=qs,
        )
        self._motor_name = motor_name
        self._detector_name = detector_name
        self.re_manager = qs
        self._seen_uids = []

    def measurement_plan(self, point: ArrayLike) -> Tuple[str, list, dict]:
        "Ignore point and do the same scan every time."
        return "scan", [[self._detector_name], self._motor_name, -1, 1, 10], dict()

    def unpack_run(self, run) -> Tuple[Union[float, ArrayLike], Union[float, ArrayLike]]:
        "Ignore the run and return dummy data."
        self._seen_uids.append(run.metadata["start"]["uid"])
        return 0, 0

    def tell(self, x, y) -> Dict:
        "Simple dict of dummy data and current attrs"
        return dict(x=x, y=y, motor=self._motor_name, detector=self._detector_name)

    def ask(self, batch_size: int = 1) -> Tuple[Sequence[dict[str, ArrayLike]], Sequence[ArrayLike]]:
        docs, proposals = [], []
        for _ in range(batch_size):
            n1, n2 = self._create_dummy_data()
            proposals.append(0)
            docs.append(
                dict(motor=self._motor_name, detector=self._detector_name, strategy="dumb", noise1d=n1, noise2d=n2)
            )
        return docs, proposals

    def report(self, **kwargs) -> dict:
        "Simple report of current attrs with some dummy data."
        n1, n2 = self._create_dummy_data()
        return dict(
            motor=self._motor_name,
            detector=self._detector_name,
            next_big_thing="avacado toast",
            noise1d=n1,
            noise2d=n2,
        )

    @staticmethod
    def _create_dummy_data():
        """Returns a random 1d and 2d numpy array shape (10,) and (10, 10)"""
        return np.random.rand(10), np.random.rand(10, 10)

    def name(self) -> str:
        return "MVPFullStackAgent"

    def server_registrations(self) -> None:
        register_variable("motor", self, "_motor_name")
        register_variable("detector", self, "_detector_name")
        register_variable("seen_uids", self, "_seen_uids")
        return super().server_registrations()


agent = MVPFullStackAgent()


@startup_decorator
def startup_agent():
    if not agent.re_manager.status()["worker_environment_exists"]:
        agent.re_manager.environment_open()
    agent.start()


@shutdown_decorator
def shutdown_agent():
    return agent.stop()
