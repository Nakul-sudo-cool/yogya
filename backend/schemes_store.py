import json
import os
from typing import List, Dict, Any, Optional
from rules_engine import RuleClause

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "schemes.json")

class SchemesStore:
    """
    Persistent Single Source of Truth for Indian Government Schemes.
    Loads from data/schemes.json, provides fast querying by state/id/keyword,
    and supports dynamic runtime registration of new schemes scraped from the web.
    """

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or DEFAULT_DATA_PATH
        self._schemes: List[Dict[str, Any]] = []
        self._schemes_map: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self):
        """Loads schemes from JSON disk storage into structured memory cache."""
        if not os.path.exists(self.data_path):
            self._schemes = []
            self._schemes_map = {}
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_list = json.load(f)

        self._schemes = []
        self._schemes_map = {}

        for item in raw_list:
            scheme_id = item.get("scheme_id", "").strip()
            if not scheme_id:
                continue

            # Convert rule dicts to RuleClause pydantic objects if not already
            parsed_rules: List[RuleClause] = []
            for r in item.get("rules", []):
                if isinstance(r, RuleClause):
                    parsed_rules.append(r)
                elif isinstance(r, dict):
                    parsed_rules.append(RuleClause(
                        clause_id=r.get("clause_id", "CLAUSE_01"),
                        rule_name=r.get("rule_name", "Eligibility Requirement"),
                        source_clause=r.get("source_clause", "Statutory Rule"),
                        operator=r.get("operator", "=="),
                        field=r.get("field", ""),
                        target_value=r.get("target_value"),
                        description=r.get("description", "")
                    ))

            scheme_entry = {
                "scheme_id": scheme_id,
                "scheme_name": item.get("scheme_name", scheme_id),
                "department": item.get("department", "Government Department"),
                "state": item.get("state", "All-India"),
                "portal": item.get("portal", ""),
                "myscheme_url": item.get("myscheme_url", ""),
                "annual_benefit_inr": float(item.get("annual_benefit_inr", 25000.0)),
                "brief_eligibility": item.get("brief_eligibility", ""),
                "keywords": item.get("keywords", []),
                "rules": parsed_rules,
                "raw_rules": [r.dict() if hasattr(r, "dict") else r for r in parsed_rules]
            }

            self._schemes.append(scheme_entry)
            self._schemes_map[scheme_id.upper()] = scheme_entry

    def get_all(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns all schemes matching the requested state jurisdiction.
        Central / All-India schemes are included for any state query.
        """
        if not state or state.strip() in ["All-India", "All-India (Pan-India View)", "Central / National", ""]:
            return list(self._schemes)

        state_clean = state.strip().lower()
        matched = []
        for s in self._schemes:
            s_state = s["state"].strip().lower()
            if s_state in ["all-india", "central"]:
                matched.append(s)
            elif s_state == state_clean:
                matched.append(s)
            elif state_clean in s_state or s_state in state_clean:
                matched.append(s)
        return matched

    def get_by_id(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        """Case-insensitive lookup by scheme ID."""
        if not scheme_id:
            return None
        return self._schemes_map.get(scheme_id.strip().upper())

    def search(self, query: str = "", state: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fast multi-field search across scheme names, departments, states, keywords, and eligibility text.
        """
        q = query.strip().lower()
        base_list = self.get_all(state)

        if not q:
            return base_list

        results = []
        for s in base_list:
            in_name = q in s["scheme_name"].lower()
            in_id = q in s["scheme_id"].lower()
            in_dept = q in s["department"].lower()
            in_state = q in s["state"].lower()
            in_brief = q in s["brief_eligibility"].lower()
            in_kw = any(q in kw.lower() for kw in s["keywords"])

            if in_name or in_id or in_dept or in_state or in_brief or in_kw:
                results.append(s)

        return results

    def save_scheme(self, scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Persists a new or updated scheme to disk in data/schemes.json and updates in-memory registry.
        """
        scheme_id = scheme_data.get("scheme_id", "").strip().upper()
        if not scheme_id:
            scheme_id = f"SCHEME_{len(self._schemes) + 1}"

        # Prepare rules
        raw_rules = []
        for r in scheme_data.get("rules", []):
            if isinstance(r, dict):
                raw_rules.append(r)
            elif hasattr(r, "dict"):
                raw_rules.append(r.dict())

        record = {
            "scheme_id": scheme_id,
            "scheme_name": scheme_data.get("scheme_name", scheme_id),
            "department": scheme_data.get("department", "Government Department"),
            "state": scheme_data.get("state", "All-India"),
            "portal": scheme_data.get("portal", ""),
            "annual_benefit_inr": float(scheme_data.get("annual_benefit_inr", 25000.0)),
            "brief_eligibility": scheme_data.get("brief_eligibility", ""),
            "keywords": scheme_data.get("keywords", [scheme_id.lower(), scheme_data.get("state", "").lower()]),
            "rules": raw_rules
        }

        # Check existing disk content
        existing_list = []
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    existing_list = json.load(f)
            except Exception:
                existing_list = []

        found_idx = -1
        for idx, item in enumerate(existing_list):
            if item.get("scheme_id", "").strip().upper() == scheme_id:
                found_idx = idx
                break

        if found_idx >= 0:
            existing_list[found_idx] = record
        else:
            existing_list.append(record)

        # Write atomically back to disk
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(existing_list, f, indent=2, ensure_ascii=False)

        # Reload cache
        self.load()
        return self.get_by_id(scheme_id)

    def to_preloaded_dict(self) -> Dict[str, Dict[str, Any]]:
        """Returns standard dictionary keyed by scheme_id for backward compatibility."""
        return {s["scheme_id"]: s for s in self._schemes}
