from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class TestStatus(enum.Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class TestScenario(Base):
    __tablename__ = "test_scenarios"

    scenario_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    priority = Column(String)

    steps = relationship("TestStep", cascade="all, delete-orphan")
    results = relationship("TestResult", cascade="all, delete-orphan")


class TestStep(Base):
    __tablename__ = "test_steps"

    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("test_scenarios.scenario_id"))
    step_number = Column(Integer)
    action = Column(String)
    expected_result = Column(String)


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("test_scenarios.scenario_id"))
    execution_date = Column(Date)
    status = Column(Enum(TestStatus))
    comment = Column(String)

    type = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "base",
        "polymorphic_on": type
    }


class ManualTestResult(TestResult):
    __tablename__ = "manual_results"

    id = Column(Integer, ForeignKey("test_results.id"), primary_key=True)
    tester_name = Column(String)
    environment = Column(String)
    build_version = Column(String)
    actual_result = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "manual"
    }


class AutomatedTestResult(TestResult):
    __tablename__ = "automated_results"

    id = Column(Integer, ForeignKey("test_results.id"), primary_key=True)
    framework = Column(String)
    execution_time = Column(Integer)
    log_file = Column(String)
    ci_pipeline = Column(String)
    actual_result = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "auto"
    }