import magicgenerator
import pytest
import logging
import os

def test_load_valid_schema_from_cli():
    assert magicgenerator.load_schema("{\"age\": \"int:rand(1, 90)\"}") == {"age": "int:rand(1, 90)"}

invalid_data_schemas = [("{\"age\"= \"int:rand(1, 90)\"}", "Invalid data schema or invalid path to json file."),
                        ("{\"pet\": \"str:cat\"", "Invalid data schema or invalid path to json file.")]

@pytest.mark.parametrize(('schema', 'message'), invalid_data_schemas)
def test_load_inavlid_schema_from_cli(schema, message, caplog):
    with caplog.at_level(logging.ERROR):
        with pytest.raises(SystemExit):
            magicgenerator.load_schema(schema)
        assert message in caplog.text 

@pytest.fixture
def files_to_test_load_schema(tmp_path):
    path = tmp_path / "to_test_load_schema"
    path.mkdir()
    valid_file = path / "valid_data_schema.json"
    invalid_file = path / "invalid_data_schema.json"
    valid_file.write_text("{\"name\": \"str:rand\", \"number\" : \"int:56\"}")
    invalid_file.write_text("{\"name\": \"str:rand\", \"number\", \"int:56\"}")
    return valid_file, invalid_file

def test_load_schema_from_file(files_to_test_load_schema):
    assert magicgenerator.load_schema(files_to_test_load_schema[0]) == {"name": "str:rand", "number" : "int:56"}
    with pytest.raises(SystemExit):
        magicgenerator.load_schema(files_to_test_load_schema[1])

valid_data_types = [({"date": "timestamp:"}),
                    ({"name": "str:rand"}),
                    ({"age": "int:rand(1, 90)"}),
                    ({"type": "str:['client', 'partner']", "pet": "str:cat", "empty_value": "int:"})]

@pytest.mark.parametrize(('json_str'), valid_data_types)
def test_check_schema_valid_type(json_str):
    assert magicgenerator.check_data_schema(json_str) is None

invalid_data_types = [({"type": "list:['client', 'partner']"}, "Type could be: timestamp, str and int, not list."),
                      ({"age": "tuple:rand(1, 90)"}, "Type could be: timestamp, str and int, not tuple."),
                      ({"pet": "int:cat"}, "cat does not have an int type."),
                      ({"random": "str:rand(2, 6)"}, "rand(from, to) possible to use only with 'int' type.")]

@pytest.mark.parametrize(('schema', 'message'), invalid_data_types)
def test_check_schema_invalid_type(schema, message, caplog):
    with caplog.at_level(logging.ERROR):
        with pytest.raises(SystemExit):
            magicgenerator.check_data_schema(schema) 
        assert message in caplog.text

def test_generate_one_line():
    assert magicgenerator.generate_one_line({"type": "int:[2]", "pet": "str:cat", "empty": "int:"}) == {"type": 2, "pet": "cat", "empty": None}

@pytest.fixture
def temporary_path(tmp_path):
    path = tmp_path / "generated"
    path.mkdir()
    for i in range(5):
        file = path / f"generated_data_{i}.json"
        file.write_text("{}")
    return path

def test_clear(temporary_path):
    assert len(os.listdir(temporary_path)) == 5
    magicgenerator.clear(temporary_path, "generated_data")
    assert len(os.listdir(temporary_path)) == 0

def test_safe_to_one_file(temporary_path, caplog):
    magicgenerator.safe_to_one_file([temporary_path, [{"age": 56, "name": "Tom"}], "generated_data_5.json"])
    file = temporary_path / "generated_data_5.json"
    assert file.read_text() == '{"age": 56, "name": "Tom"}\n'
    with caplog.at_level(logging.ERROR):
        with pytest.raises(SystemExit):
            magicgenerator.safe_to_one_file([file, [{"age": 56, "name": "Tom"}], "generated_data_6.json"])
        assert "Path exist but it is not a directory." in caplog.text

def test_safe_data(tmpdir):
    assert len(os.listdir(tmpdir)) == 0
    magicgenerator.safe_data({"name": "str:rand", "age": "int:rand(1, 90)"}, "generated_data", tmpdir, 'uuid', 40, False, 1, 8)
    assert len(os.listdir(tmpdir)) == 40

def test_data_lines_in_files(tmpdir):
    magicgenerator.safe_data({"name": "str:rand"}, "generated_data", tmpdir, 'count', 40, True, 14, 4)
    with open(f"{tmpdir}/generated_data_0.json") as f:
        lines = f.readlines()
        assert len(lines) == 14