from app.services.parser.base import ResumeParser


class DummyParser(ResumeParser):
    def parse(self, text: str):
        return {"skills": ["Python"]}


def test_parser_contract():
    parser = DummyParser()
    result = parser.parse("Sample resume text")
    assert "skills" in result

def test_parser_contract_enforced():
    assert hasattr(ResumeParser, "parse")