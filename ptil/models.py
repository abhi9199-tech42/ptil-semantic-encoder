from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any


class ROOT(Enum):
    MOTION = "MOTION"
    TRANSFER = "TRANSFER"
    COMMUNICATION = "COMMUNICATION"
    COGNITION = "COGNITION"
    PERCEPTION = "PERCEPTION"
    CREATION = "CREATION"
    DESTRUCTION = "DESTRUCTION"
    CHANGE = "CHANGE"
    POSSESSION = "POSSESSION"
    INTENTION = "INTENTION"
    EXISTENCE = "EXISTENCE"
    EMOTION = "EMOTION"
    DESIRE = "DESIRE"
    PREFERENCE = "PREFERENCE"
    JOY = "JOY"
    SADNESS = "SADNESS"
    ANGER = "ANGER"
    FEAR = "FEAR"
    EVALUATION = "EVALUATION"
    COMPARISON = "COMPARISON"
    JUDGMENT = "JUDGMENT"
    APPROVAL = "APPROVAL"
    CRITICISM = "CRITICISM"
    SOCIAL = "SOCIAL"
    COOPERATION = "COOPERATION"
    CONFLICT = "CONFLICT"
    AGREEMENT = "AGREEMENT"
    PROMISE = "PROMISE"
    THREAT = "THREAT"
    REQUEST = "REQUEST"
    CAUSATION = "CAUSATION"
    PREVENTION = "PREVENTION"
    ENABLEMENT = "ENABLEMENT"
    ATTEMPT = "ATTEMPT"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ANALYSIS = "ANALYSIS"
    MEMORY = "MEMORY"
    LEARNING = "LEARNING"
    TEACHING = "TEACHING"
    DECISION = "DECISION"
    BELIEF = "BELIEF"
    STATE = "STATE"
    PROPERTY = "PROPERTY"
    QUANTITY = "QUANTITY"
    TIME_RELATION = "TIME_RELATION"
    LOCATION_STATE = "LOCATION_STATE"
    EXPERIENCE = "EXPERIENCE"
    ASSISTANCE = "ASSISTANCE"
    TRAVEL = "TRAVEL"
    CAUSE_EFFECT = "CAUSE_EFFECT"
    ACTION = "ACTION"
    CONSUMPTION = "CONSUMPTION"
    REFUSAL = "REFUSAL"


class Operator(Enum):
    PAST = "PAST"
    PRESENT = "PRESENT"
    FUTURE = "FUTURE"
    CONTINUOUS = "CONTINUOUS"
    COMPLETED = "COMPLETED"
    HABITUAL = "HABITUAL"
    NEGATION = "NEGATION"
    AFFIRMATION = "AFFIRMATION"
    POSSIBLE = "POSSIBLE"
    NECESSARY = "NECESSARY"
    OBLIGATORY = "OBLIGATORY"
    PERMITTED = "PERMITTED"
    CAUSATIVE = "CAUSATIVE"
    SELF_INITIATED = "SELF_INITIATED"
    FORCED = "FORCED"
    DIRECTION_IN = "DIRECTION_IN"
    DIRECTION_OUT = "DIRECTION_OUT"
    TOWARD = "TOWARD"
    AWAY = "AWAY"


class Role(Enum):
    AGENT = "AGENT"
    PATIENT = "PATIENT"
    THEME = "THEME"
    GOAL = "GOAL"
    SOURCE = "SOURCE"
    INSTRUMENT = "INSTRUMENT"
    LOCATION = "LOCATION"
    TIME = "TIME"
    EXPERIENCER = "EXPERIENCER"
    STIMULUS = "STIMULUS"
    STANDARD = "STANDARD"
    VERDICT = "VERDICT"
    RESULT = "RESULT"
    PATH = "PATH"
    ATTRIBUTE = "ATTRIBUTE"
    VALUE = "VALUE"
    COMPARISON = "COMPARISON"
    CONTENT = "CONTENT"
    MANNER = "MANNER"


class META(Enum):
    ASSERTIVE = "ASSERTIVE"
    QUESTION = "QUESTION"
    COMMAND = "COMMAND"
    UNCERTAIN = "UNCERTAIN"
    EVIDENTIAL = "EVIDENTIAL"
    EMOTIVE = "EMOTIVE"
    IRONIC = "IRONIC"


@dataclass
class Entity:
    text: str
    normalized: str


@dataclass
class LinguisticAnalysis:
    tokens: List[str]
    pos_tags: List[str]
    dependencies: List[Tuple[int, str, int]]
    negation_markers: List[int]
    tense_markers: Dict[str, List[int]]
    aspect_markers: Dict[str, List[int]]
    lemmas: List[str] = field(default_factory=list)
    doc: Optional[Any] = None


@dataclass
class CSC:
    root: ROOT
    ops: List[Operator]
    roles: Dict[Role, Entity]
    meta: Optional[META] = None
