"""JMeter sources."""

from ..meta.entity import EntityAttributeType
from ..meta.source import Source
from ..parameters import IntegerParameter, access_parameters, MultipleChoiceWithAdditionParameter, SingleChoiceParameter


ALL_JMETER_METRICS = ["slow_transactions"]

TRANSACTIONS_TO_IGNORE = MultipleChoiceWithAdditionParameter(
    name="Transactions to ignore (regular expressions or transaction names)",
    short_name="transactions to ignore",
    help="Transactions to ignore can be specified by transaction name or by regular expression.",
    metrics=ALL_JMETER_METRICS,
)

TRANSACTIONS_TO_INCLUDE = MultipleChoiceWithAdditionParameter(
    name="Transactions to include (regular expressions or transaction names)",
    short_name="transactions to include",
    help="Transactions to include can be specified by transaction name or by regular expression.",
    placeholder="all",
    metrics=ALL_JMETER_METRICS,
)

TARGET_RESPONSE_TIME = IntegerParameter(
    name="Target response time",
    short_name="target response time",
    help="The response times of the transactions should be less than or equal to the target response time.",
    default_value="1000",
    unit="milliseconds",
    metrics=ALL_JMETER_METRICS,
)

PERCENTILE_90 = "90th percentile"

RESPONSE_TIME_TO_EVALUATE = SingleChoiceParameter(
    name="Response time type to evaluate against the target response time",
    short_name="response time type to evaluate",
    help="Which response time type to compare with the target response time to determine slow transactions.",
    default_value=PERCENTILE_90,
    values=[PERCENTILE_90, "mean", "median", "minimum", "maximum"],
    api_values={
        PERCENTILE_90: "percentile_90_response_time",
        "mean": "mean_response_time",
        "median": "median_response_time",
        "minimum": "min_response_time",
        "maximum": "max_response_time",
    },
    metrics=ALL_JMETER_METRICS,
)

JMETER_JSON = Source(
    name="JMeter JSON",
    description="Apache JMeter application is open source software, a 100% pure Java application designed to load "
    "test functional behavior and measure performance.",
    url="https://jmeter.apache.org",
    parameters=dict(
        target_response_time=TARGET_RESPONSE_TIME,
        response_time_to_evaluate=RESPONSE_TIME_TO_EVALUATE,
        transactions_to_ignore=TRANSACTIONS_TO_IGNORE,
        transactions_to_include=TRANSACTIONS_TO_INCLUDE,
        **access_parameters(ALL_JMETER_METRICS, source_type="JMeter report", source_type_format="JSON")
    ),
    entities=dict(
        slow_transactions=dict(
            name="slow transaction",
            attributes=[
                dict(name="Transactions", key="name"),
                dict(name="Sample count", type=EntityAttributeType.INTEGER),
                dict(name="Error count", type=EntityAttributeType.INTEGER),
                dict(name="Error percentage", type=EntityAttributeType.FLOAT),
                dict(name="Mean response time (ms)", key="mean_response_time", type=EntityAttributeType.FLOAT),
                dict(name="Median response time (ms)", key="median_response_time", type=EntityAttributeType.FLOAT),
                dict(name="Minimum response time (ms)", key="min_response_time", type=EntityAttributeType.FLOAT),
                dict(name="Maximum response time (ms)", key="max_response_time", type=EntityAttributeType.FLOAT),
                dict(
                    name="90th percentile response time (ms)",
                    key="percentile_90_response_time",
                    type=EntityAttributeType.FLOAT,
                ),
            ],
        )
    ),
)