from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CitizenProfile(BaseModel):
    citizen_name: str
    age: int
    family_income: float
    caste_category: str  # "SC", "ST", "OBC", "General", "EWS"
    is_karnataka_domicile: bool
    domicile_years: int
    education_level: str  # "10th", "12th", "Undergraduate", "Postgraduate"
    marks_percentage: float
    has_income_certificate: bool
    has_caste_certificate: bool
    has_domicile_certificate: bool
    gender: Optional[str] = "Female"
    is_farmer_child: Optional[bool] = False
    is_worker_child: Optional[bool] = False
    is_hostel_resident: Optional[bool] = False
    state_of_domicile: Optional[str] = "Karnataka"
    is_technical_course: Optional[bool] = True
    studied_govt_school: Optional[bool] = False
    dynamic_attributes: Dict[str, Any] = Field(default_factory=dict)

class RuleClause(BaseModel):
    clause_id: str
    rule_name: str
    source_clause: str
    operator: str  # "<=", ">=", "==", "in", "bool"
    field: str
    target_value: Any
    description: str

class RuleEvaluationResult(BaseModel):
    clause_id: str
    rule_name: str
    source_clause: str
    passed: bool
    actual_value: Any
    expected_condition: str
    status_badge: str  # "✅ PASS" or "❌ FAIL" or "⚠️ UNKNOWN"
    remediation_step: Optional[str] = None

class SchemeEvaluationSummary(BaseModel):
    scheme_id: str
    scheme_name: str
    department: str
    annual_benefit_inr: float
    overall_verdict: str  # "ELIGIBLE", "INELIGIBLE", "MISSING_DOCUMENTS"
    results: List[RuleEvaluationResult]
    missing_documents: List[str]
    shortest_path_action_plan: List[str]
    portal: Optional[str] = ""
    myscheme_url: Optional[str] = ""


class DeterministicRulesEngine:
    """
    Pure Python Deterministic Prover Engine:
    Zero hallucinations. Evaluates citizen parameters against strict policy clauses.
    Supports statutory preloaded schemes, dynamically compiled rules from circulars,
    and open-ended extensible attribute bags.
    """

    @staticmethod
    def evaluate_clause(clause: RuleClause, profile: CitizenProfile) -> RuleEvaluationResult:
        # Map common field aliases extracted by LLM
        field = clause.field.strip().lower() if clause.field else ""
        if field in ["income", "annual_income", "family_income", "household_income"]:
            field = "family_income"
        elif field in ["marks", "marks_percentage", "percentage", "aggregate", "score"]:
            field = "marks_percentage"
        elif field in ["domicile_years", "years_in_state", "residency_years", "domicile_duration"]:
            field = "domicile_years"
        elif field in ["domicile", "is_karnataka_domicile", "karnataka_domicile", "resident"]:
            # If target value is a number > 1 (e.g. 7 years), map to domicile_years
            try:
                if float(clause.target_value) > 1:
                    field = "domicile_years"
                else:
                    field = "is_karnataka_domicile"
            except (ValueError, TypeError):
                field = "is_karnataka_domicile"
        elif field in ["caste", "caste_category", "category", "reservation"]:
            field = "caste_category"
        elif field in ["education", "education_level", "degree", "qualification", "course_level"]:
            field = "education_level"
        elif field in ["age", "candidate_age"]:
            field = "age"
        elif field in ["state", "state_of_domicile", "domicile_state", "state_domicile"]:
            field = "state_of_domicile"
        elif field in ["gender", "sex"]:
            field = "gender"
        elif field in ["farmer", "is_farmer_child", "farmer_child"]:
            field = "is_farmer_child"
        elif field in ["worker", "labour", "is_worker_child", "worker_child"]:
            field = "is_worker_child"
        elif field in ["hostel", "is_hostel_resident", "govt_hostel"]:
            field = "is_hostel_resident"
        elif field in ["technical", "is_technical_course", "aicte_approved"]:
            field = "is_technical_course"
        elif field in ["govt_school", "studied_govt_school", "government_school"]:
            field = "studied_govt_school"

        # Resolve actual value from standard profile attributes or dynamic extensible bag
        actual = getattr(profile, field, None)
        if actual is None and hasattr(profile, "dynamic_attributes") and profile.dynamic_attributes:
            actual = profile.dynamic_attributes.get(field, None)
            if actual is None and clause.field:
                actual = profile.dynamic_attributes.get(clause.field, None)

        # Cross-field bridge: if testing is_karnataka_domicile and state_of_domicile is Karnataka
        if field == "is_karnataka_domicile" and actual is None:
            if (profile.state_of_domicile or "").strip().lower() == "karnataka":
                actual = True
            else:
                actual = profile.is_karnataka_domicile

        passed = False
        remediation = None

        if clause.operator == "<=":
            try:
                act_num = float(actual) if actual is not None else None
                tgt_num = float(clause.target_value)
                passed = act_num is not None and act_num <= tgt_num
                cond = f"Must be <= {tgt_num:,.0f}" if tgt_num >= 1000 else f"Must be <= {tgt_num}"
                if not passed:
                    diff = act_num - tgt_num if act_num is not None else tgt_num
                    remediation = f"Current {field} exceeds limit by {diff:,.1f}."
            except Exception:
                passed = False
                cond = f"Must be <= {clause.target_value}"
                remediation = f"Comparison failed for {field}."

        elif clause.operator == ">=":
            try:
                act_num = float(actual) if actual is not None else None
                tgt_num = float(clause.target_value)
                passed = act_num is not None and act_num >= tgt_num
                cond = f"Must be >= {tgt_num:,.0f}" if tgt_num >= 1000 else f"Must be >= {tgt_num}"
                if not passed:
                    diff = tgt_num - act_num if act_num is not None else tgt_num
                    remediation = f"Current {field} is below required threshold by {diff:,.1f}."
            except Exception:
                passed = False
                cond = f"Must be >= {clause.target_value}"
                remediation = f"Comparison failed for {field}."

        elif clause.operator == "==":
            tgt_str = str(clause.target_value).strip().lower()
            if field == "state_of_domicile" and tgt_str in ["all-india", "central", "pan-india", "india", "any"]:
                passed = True
                cond = "Open to all Indian States"
            elif field == "is_karnataka_domicile" and (profile.state_of_domicile or "").lower() == "karnataka":
                passed = True if tgt_str in ["true", "1", "yes"] else False
                cond = "Must be Karnataka Domicile"
            elif isinstance(clause.target_value, bool) or tgt_str in ["true", "false"]:
                tgt_bool = True if tgt_str == "true" else False
                act_bool = True if str(actual).lower() in ["true", "1", "yes"] else False if str(actual).lower() in ["false", "0", "no"] else bool(actual)
                passed = (act_bool == tgt_bool)
                cond = f"Must be verified {tgt_bool}"
            else:
                passed = str(actual).strip().lower() == tgt_str
                cond = f"Must be equal to {clause.target_value}"
            if not passed:
                remediation = f"Expected '{clause.target_value}', but current profile has '{actual}'."

        elif clause.operator == "in":
            if isinstance(clause.target_value, list):
                passed = any(str(actual).strip().lower() == str(t).strip().lower() for t in clause.target_value)
            else:
                passed = str(actual).strip().lower() in str(clause.target_value).strip().lower()
            cond = f"Must be one of {clause.target_value}"
            if not passed:
                remediation = f"Value '{actual}' is not eligible under required category {clause.target_value}."

        elif clause.operator == "bool":
            passed = bool(actual) is True
            cond = "Required to be verified True"
            if not passed:
                remediation = f"Missing required verification for {clause.rule_name} ({field})."
        else:
            cond = f"Condition: {clause.operator} {clause.target_value}"
            remediation = "Undefined operator evaluation."

        return RuleEvaluationResult(
            clause_id=clause.clause_id,
            rule_name=clause.rule_name,
            source_clause=clause.source_clause,
            passed=passed,
            actual_value=actual,
            expected_condition=cond,
            status_badge="✅ PASS" if passed else "❌ FAIL",
            remediation_step=remediation
        )

    @staticmethod
    def evaluate_scheme(scheme_id: str, scheme_name: str, department: str, benefit: float,
                        rules: List[RuleClause], profile: CitizenProfile,
                        portal: str = "", myscheme_url: str = "") -> SchemeEvaluationSummary:
        results = [DeterministicRulesEngine.evaluate_clause(rule, profile) for rule in rules]
        
        # Check doc gaps dynamically based on citizen's domicile jurisdiction
        state = profile.state_of_domicile or "Karnataka"
        missing_docs = []
        if not profile.has_income_certificate and profile.family_income <= 250000:
            if state.lower() == "karnataka":
                missing_docs.append("Valid Tahsildar Income Certificate (Form 16 / RD Number)")
            elif state.lower() == "maharashtra":
                missing_docs.append("Tahsildar Income Certificate via Aaple Sarkar Portal")
            elif state.lower() == "tamil nadu":
                missing_docs.append("Income Certificate from Revenue Dept via e-Sevai Kendra")
            else:
                missing_docs.append(f"Official Revenue Dept Income Certificate ({state})")

        if not profile.has_caste_certificate and profile.caste_category in ["SC", "ST", "OBC"]:
            missing_docs.append(f"Caste / Community Certificate issued by {state} Competent Authority")

        if not profile.has_domicile_certificate:
            missing_docs.append(f"Permanent Domicile / Residence Certificate ({state})")

        all_passed = all(r.passed for r in results)
        
        if all_passed and not missing_docs:
            verdict = "ELIGIBLE"
        elif any(not r.passed and r.clause_id not in ["DOC_INC", "DOC_CST", "DOC_DOM", "SSP_04", "VS_04"] for r in results):
            verdict = "INELIGIBLE"
        else:
            verdict = "MISSING_DOCUMENTS"

        # Action Plan
        action_plan = []
        if verdict == "ELIGIBLE":
            action_plan.append("Generate signed verification packet.")
            action_plan.append("Proceed to Human Authorization Gate for official portal dispatch.")
        elif verdict == "MISSING_DOCUMENTS":
            for d in missing_docs:
                action_plan.append(f"Apply for {d} at nearest public service center (Seva Sindhu / Bangalore One / Aaple Sarkar / e-Sevai).")
            action_plan.append("Expected turnaround: 5-7 working days before scheme deadline.")
        else:
            action_plan.append("Citizen does not meet statutory eligibility parameters (Income/Marks/Age threshold).")

        return SchemeEvaluationSummary(
            scheme_id=scheme_id,
            scheme_name=scheme_name,
            department=department,
            annual_benefit_inr=benefit,
            overall_verdict=verdict,
            results=results,
            missing_documents=missing_docs,
            shortest_path_action_plan=action_plan,
            portal=portal,
            myscheme_url=myscheme_url
        )

