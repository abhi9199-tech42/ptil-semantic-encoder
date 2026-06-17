from typing import Dict, List, Optional, Set, Tuple, TYPE_CHECKING
from .models import ROOT, Role, Entity, LinguisticAnalysis
from .compatibility import is_role_compatible, get_compatible_roles

if TYPE_CHECKING:
    from spacy.tokens import Token


class ROLESBinder:
    """
    Binds entities to semantic roles using the spaCy Doc from LinguisticAnalysis.
    """

    def bind_roles(self, analysis: LinguisticAnalysis, root: ROOT) -> Dict[Role, Entity]:
        if not analysis.tokens:
            return {}

        doc = getattr(analysis, 'doc', None)
        if doc is None:
            return {}

        roles = {}
        compatible_roles = get_compatible_roles(root)

        main_verb = self._find_main_verb(doc)
        if not main_verb:
            return roles

        subject_entity = self._bind_subject_to_agent(doc, main_verb, compatible_roles)
        if subject_entity:
            roles[Role.AGENT] = subject_entity

        object_roles = self._bind_objects_to_roles(doc, main_verb, root, compatible_roles)
        roles.update(object_roles)

        passive_roles = self._bind_passive_subject(doc, main_verb, root, compatible_roles, roles)
        roles.update(passive_roles)

        prep_roles = self._bind_prepositional_phrases(doc, main_verb, compatible_roles)
        roles.update(prep_roles)

        return self._validate_role_compatibility(roles, root)

    def _find_main_verb(self, doc) -> Optional['Token']:
        for token in doc:
            if token.dep_ == "ROOT":
                if token.pos_ in ["VERB", "AUX"]:
                    return token
                elif token.pos_ == "NOUN":
                    return token

        for token in doc:
            if token.pos_ == "VERB":
                return token

        return None

    def _bind_subject_to_agent(self, doc, main_verb: 'Token',
                               compatible_roles: Set[Role]) -> Optional[Entity]:
        if Role.AGENT not in compatible_roles:
            return None

        subject_deps = {"nsubj", "csubj"}

        for token in doc:
            if token.head == main_verb and token.dep_ in subject_deps:
                subject_text = self._extract_noun_phrase(token)
                return Entity(
                    text=subject_text,
                    normalized=token.lemma_.lower()
                )

        if main_verb.pos_ in ["NOUN", "PROPN"]:
            fallback_deps = {"compound", "poss", "nmod"}
            for token in doc:
                if token.head == main_verb and token.dep_ in fallback_deps:
                    if token.pos_ in ["NOUN", "PROPN", "PRON"]:
                        subject_text = self._extract_noun_phrase(token)
                        return Entity(
                            text=subject_text,
                            normalized=token.lemma_.lower()
                        )

        return None

    def _bind_objects_to_roles(self, doc, main_verb: 'Token', root: ROOT,
                               compatible_roles: Set[Role]) -> Dict[Role, Entity]:
        roles = {}
        object_deps = {"dobj", "pobj", "iobj"}

        for token in doc:
            if token.head == main_verb and token.dep_ in object_deps:
                object_text = self._extract_noun_phrase(token)
                entity = Entity(
                    text=object_text,
                    normalized=token.lemma_.lower()
                )
                role = self._select_object_role(root, compatible_roles, roles)
                if role:
                    roles[role] = entity

        return roles

    def _select_object_role(self, root: ROOT, compatible_roles: Set[Role],
                            existing_roles: Dict[Role, Entity]) -> Optional[Role]:
        object_role_priority = [Role.PATIENT, Role.THEME]

        for role in object_role_priority:
            if role in compatible_roles and role not in existing_roles:
                return role

        return None

    def _bind_passive_subject(self, doc, main_verb: 'Token', root: ROOT,
                              compatible_roles: Set[Role], existing_roles: Dict[Role, Entity]) -> Dict[Role, Entity]:
        roles = {}
        passive_deps = {"nsubjpass", "csubjpass"}

        for token in doc:
            if token.head == main_verb and token.dep_ in passive_deps:
                subject_text = self._extract_noun_phrase(token)
                entity = Entity(
                    text=subject_text,
                    normalized=token.lemma_.lower()
                )
                role = self._select_object_role(root, compatible_roles, {**existing_roles, **roles})
                if role:
                    roles[role] = entity

        return roles

    def _bind_prepositional_phrases(self, doc, main_verb: 'Token',
                                    compatible_roles: Set[Role]) -> Dict[Role, Entity]:
        roles = {}

        prep_role_map = {
            "to": Role.GOAL,
            "into": Role.GOAL,
            "toward": Role.GOAL,
            "towards": Role.GOAL,
            "from": Role.SOURCE,
            "out": Role.SOURCE,
            "off": Role.SOURCE,
            "at": Role.LOCATION,
            "in": Role.LOCATION,
            "on": Role.LOCATION,
            "under": Role.LOCATION,
            "over": Role.LOCATION,
            "beside": Role.LOCATION,
            "near": Role.LOCATION,
            "during": Role.TIME,
            "before": Role.TIME,
            "after": Role.TIME,
            "while": Role.TIME,
            "with": Role.INSTRUMENT,
            "by": Role.INSTRUMENT,
            "using": Role.INSTRUMENT,
        }

        for token in doc:
            if token.pos_ == "ADP":
                prep_text = token.text.lower()
                role = prep_role_map.get(prep_text)
                if not role or role not in compatible_roles or role in roles:
                    continue

                prep_object = None
                for child in token.children:
                    if child.dep_ == "pobj":
                        prep_object = child
                        break

                if prep_object:
                    object_text = self._extract_noun_phrase(prep_object)
                    roles[role] = Entity(
                        text=object_text,
                        normalized=prep_object.lemma_.lower()
                    )

        return roles

    def _extract_noun_phrase(self, token: 'Token') -> str:
        if token.pos_ in ["NOUN", "PROPN", "PRON"]:
            left_bound = token.left_edge.i
            right_bound = token.right_edge.i + 1
            doc = token.doc
            return doc[left_bound:right_bound].text

        return token.text

    def _validate_role_compatibility(self, roles: Dict[Role, Entity],
                                     root: ROOT) -> Dict[Role, Entity]:
        validated_roles = {}
        for role, entity in roles.items():
            if is_role_compatible(root, role):
                validated_roles[role] = entity
        return validated_roles
