"""Request payload helper functions
"""

from copy import deepcopy


class SlotNotFoundException(Exception):
    pass


class Payload:
    def __init__(self, payload):
        self.payload = deepcopy(payload)
        self.slots = self.payload["slots"]

    def get(self):
        """Gets the current request payload

        Returns:
            dict -- The request payload
        """
        return deepcopy(self.payload)

    def overwrite(self, req):
        """Sets the current request payload
        """
        self.payload = deepcopy(req)

    def get_ids(self):
        """Gets the ID fields from the payload

        Returns:
            dict -- The ID fields
        """
        return deepcopy(
            {
                "ai_version": self.get_field("ai_version"),
                "device": self.get_field("device"),
                "dialog": self.get_field("dialog"),
                "external_user_id": self.get_field("external_user_id"),
                "qid": self.get_field("qid"),
                "session_id": self.get_field("session_id"),
            }
        )

    def get_slots(self):
        """Gets the slots from the payload

        Returns:
            dict -- The slots object
        """
        return deepcopy(self.get_field("slots"))

    def get_state(self):
        """Gets the state from the payload

        Returns:
            string -- The state name
        """
        return self.get_field("state")

    def get_intent(self):
        """Gets the intent from the payload

        Returns:
            string -- The intent name
        """
        return self.get_field("intent")

    def get_intent_probability(self):
        """Gets the intent probability from the payload

        Returns:
            decimal -- The intent probability
        """
        return self.get_field("intent_probability")

    def get_query(self):
        """Gets the query/utterance that was submitted
        to the platform from the payload

        Returns:
            string -- The query/utterance
        """
        return self.get_field("query")

    def get_time_offset(self):
        """Gets the time offset from the payload

        Returns:
            int -- The time offset
        """
        return self.get_field("time_offset")

    def get_sentiment(self):
        """Gets the sentiment from the payload

        Returns:
            int -- The sentiment where:
                -1 = negative
                 0 = neutral
                 1 = positive
        """
        return self.get_field("sentiment")

    def get_location(self):
        """Gets the latitudinal and longitudinal
        value from the payload together as location

        Returns:
            dict -- The location
        """
        return deepcopy({"lat": self.get_field("lat"), "lon": self.get_field("lon")})

    def contains_field(self, field):
        return field in self.payload

    def get_field(self, field):
        return deepcopy(self.payload[field])

    def resolve_append(self, slot_name, tuples, squash=False):
        """Resolves a set of unresolved slot values without
        modifying the existing values for a slot

        Arguments:
            slot_name {string} -- The name of the slot
            tuples {list of tuples (string, string)} -- A list
                of token, value pairs where the token is copied
                from the request and the value is constructed
                using client logic. Note that the date slot type
                does not require a value

        Returns:
            Request -- A reference to the class instance
        """
        return self._resolve(slot_name, tuples, replace=False, squash=squash)

    def resolve_replace(self, slot_name, tuples, squash=False):
        """Resolves a set of unresolved slot values and
        unresolves the currently-resolved slot values

        Arguments:
            slot_name {string} -- The name of the slot
            tuples {list of tuples (string, string)} -- A list
                of token, value pairs where the token is copied
                from the request and the value is constructed
                using client logic. Note that the date slot type
                does not require a value

        Returns:
            Request -- A reference to the class instance
        """
        return self._resolve(slot_name, tuples, replace=True, squash=squash)

    def create_slot(
        self, slot_name, slot_type, values=[], squash=False, overwrite=False
    ):
        """Creates a new slot if it does not yet exist and
        inserts a set of values

        Arguments:
            slot_name {string} -- The name of the slot
            slot_type {string} -- The type of slot

        Keyword Arguments:
            values {list} -- The slot values to insert
                into the slot and resolve. Their type is
                dependent on the slot type (default: {[]})

        Returns:
            Request -- A reference to the class instance
        """
        slot_name = self._standardize_slot_name(slot_name)
        if not self.slot_exists(slot_name):
            self.slots[slot_name] = {"type": slot_type, "values": []}
        if overwrite:
            return self.overwrite_slot_values(slot_name, values, squash=squash)
        return self.insert_slot_values(slot_name, values, squash=squash)

    def insert_slot_values(self, slot_name, values, squash=False):
        """Inserts new slot values into a slot and
        and resolves them

        Arguments:
            slot_name {string} -- The name of the slot
            values {list} -- The slot values to insert
                into the slot and resolve. Their type is
                dependent on the slot type (default: {[]})

        Returns:
            Request -- A reference to the class instance
        """
        return self._add_slot_values(
            self._try_get_slot_name(slot_name),
            self._get_slot_type(slot_name),
            values,
            replace=False,
            squash=squash,
        )

    def overwrite_slot_values(self, slot_name, values, squash=False):
        """Inserts new slot values into a slot, resolves
        them, and unresolves existing values

        Arguments:
            slot_name {string} -- The name of the slot
            values {list} -- The slot values to insert
                into the slot and resolve. Their type is
                dependent on the slot type (default: {[]})

        Returns:
            Request -- A reference to the class instance
        """
        return self._add_slot_values(
            self._try_get_slot_name(slot_name),
            self._get_slot_type(slot_name),
            values,
            replace=True,
            squash=squash,
        )

    def get_resolved_slot_values(self, slot_name):
        """Gets the resolved slot values for a given slot

        Arguments:
            slot_name {string} -- The name of the slot

        Returns:
            list -- The slot values that are currently
                resolved. Each slot value is returned as
                a dict if there are multiple fields in the
                result and as the slot type if there is only
                one field
        """
        try:
            return self._filter_slot_values(
                self._try_get_slot_name(slot_name),
                self._get_slot_values(slot_name, 1),
                self._get_slot_type(slot_name),
                resolved=True,
                blacklist=["resolved", "tokens"],
            )
        except SlotNotFoundException:
            return []

    def get_unresolved_slot_values(self, slot_name):
        """Gets the unresolved slot values for a given slot

        Arguments:
            slot_name {string} -- The name of the slot

        Returns:
            list -- The slot values that are currently
                unresolved. Each slot value is returned as
                a dict if there are multiple fields in the
                result and as the slot type if there is only
                one field
        """
        try:
            return self._filter_slot_values(
                self._try_get_slot_name(slot_name),
                self._get_slot_values(slot_name, -1),
                self._get_slot_type(slot_name),
                resolved=False,
                blacklist=["resolved"],
            )
        except SlotNotFoundException:
            return []

    def transition(self, new_state):
        """Performs a business logic transition by overriding
        the current state in the state graph

        Arguments:
            new_state {string} -- The name of the state that is
                being transitioned to

        Returns:
            Request -- A reference to the class instance
        """
        self.payload["state"] = new_state
        if self._response_slot_exists():
            self._update_response_type(new_state)
        return self

    def add_response_slot_values(self, key, value=None):
        return self._add_response_slot_generic("visuals", key, value)

    def add_response_visuals(self, key, value=None):
        return self._add_response_slot_generic("visuals", key, value)

    def add_response_speakables(self, key, value=None):
        return self._add_response_slot_generic("speakables", key, value)

    def clear_slot(self, slot_name):
        """Clears a slot by unresolving all of its slot values

        Arguments:
            slot_name {string} -- The name of the slot

        Returns:
            Request -- A reference to the class instance
        """
        try:
            slot_name = self._try_get_slot_name(slot_name)
            return self._unresolve_resolved(slot_name)
        except SlotNotFoundException:
            return self

    def slot_exists(self, slot_name):
        return self._standardize_slot_name(slot_name) in self.slots

    def _add_response_slot_generic(self, field, key, value=None):
        if value is not False and not value:
            return self._add_response_slot_field(field, deepcopy(key))
        return self._add_response_slot_field(field, {key: deepcopy(value)})

    def _add_slot_values(
        self, slot_name, slot_type, values, replace=False, squash=False
    ):
        slot_name = self._try_get_slot_name(slot_name)
        slot_type = self._get_slot_type(slot_name)
        if not isinstance(values, list):
            values = [values]
        if replace:
            self._unresolve_resolved(slot_name)
        for value in values:
            if slot_type in ["date", "dict"]:
                value["resolved"] = 1
                self.slots[slot_name]["values"].append(value)
            else:
                if squash:
                    self.slots[slot_name]["values"].append(
                        {**{"tokens": None, "resolved": 1}, **value}
                    )
                else:
                    self.slots[slot_name]["values"].append(
                        {"tokens": None, "resolved": 1, "value": value}
                    )
        return self

    def _update_response_type(self, new_state):
        self.payload["response_slots"]["response_type"] = new_state
        return self

    def _response_slot_exists(self):
        return "response_slots" in self.payload

    def _create_response_slot(self):
        if not self._response_slot_exists():
            self.payload["response_slots"] = {
                "response_type": self.payload["state"],
                "visuals": {},
                "speakables": {},
            }
        return self

    def _add_response_slot_field(self, field, slot_values):
        self._create_response_slot()
        other = "speakables"
        if field == other:
            other = "visuals"
        for key, value in slot_values.items():
            self.payload["response_slots"][field][key] = value
            if key not in self.payload["response_slots"][other]:
                self.payload["response_slots"][other][key] = value
        return self

    def _get_slot_type(self, slot_name):
        slot_name = self._try_get_slot_name(slot_name)
        return self.slots[slot_name]["type"]

    def _filter_slot_values(
        self, slot_name, slot_values, slot_type, resolved=False, blacklist=[]
    ):
        result = []
        for slot_value in slot_values:
            current = dict()
            for key, value in slot_value.items():
                if key not in blacklist:
                    current[key] = value
            if len(current.keys()) == 1:
                current = list(current.values()).pop()
            result.append(deepcopy(current))
        return result

    def _try_get_slot_name(self, slot_name):
        slot_name = self._standardize_slot_name(slot_name)
        if not self.slot_exists(slot_name):
            raise SlotNotFoundException(
                f"Slot [{slot_name}] does not exist in the payload"
            )
        return slot_name

    def _resolve(self, slot_name, tuples, replace=False, squash=False):
        slot_name = self._try_get_slot_name(slot_name)
        slot_type = self._get_slot_type(slot_name)
        unresolveds = self._get_slot_values(slot_name, -1)
        if replace:
            self._unresolve_resolved(slot_name)
        if type(tuples) != list:
            tuples = [tuples]
        for tup in tuples:
            if slot_type not in ["dict", "date"]:
                tokens, value = tup
            else:
                tokens = tup["tokens"]
            unresolved = [
                unresolved
                for unresolved in unresolveds
                if tokens == unresolved["tokens"]
            ].pop()
            if slot_type not in ["dict", "date"]:
                if isinstance(value, dict) and squash:
                    unresolved = {**unresolved, **value}
                else:
                    unresolved["value"] = value
            self._set_resolved_status(unresolved, 1)
        return self

    def _standardize_slot_name(self, slot_name):
        if not slot_name.startswith("_"):
            return f"_{slot_name.upper()}_"
        return slot_name.upper()

    def _get_slot_values(self, slot_name, resolved_status, get_all=False):
        slot_name = self._try_get_slot_name(slot_name)
        values = []
        for value in self.slots[slot_name]["values"]:
            if get_all or value["resolved"] == resolved_status:
                values.append(value)
        return values

    def _set_resolved_status(self, slot_value, resolved_status):
        slot_value["resolved"] = resolved_status

    def _unresolve_resolved(self, slot_name):
        resolved_slots = self._get_slot_values(slot_name, 1)
        for resolved_slot in resolved_slots:
            self._set_resolved_status(resolved_slot, -1)
        return self
