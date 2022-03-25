# Data generator
Console utility for generating test data based on the provided data schema. 
Note that the data schema as well as keys and values must be in double quotes (JSON syntax). String in list must be in single quotes. 
All values support notation "type:what_to_generate". Type could be: timestamp, str, int. 
Possible values of what_to_generate are 
- rand - random generation, 
- list with values - generator takes a random value from a list for each generated data line, 
- rand(from, to) - random generation for int values in the prescribed range, 
- stand alone value - use this value on each line of generated data, 
- empty value.

For timestamp type genrator ignores all values after “:”. Value for timestamp is always the current unix timestamp.

Example of data schema:

`{"date":"timestamp:", "name": "str:rand", "type":"str:['client', 'partner', 'government']", "age": "int:rand(1, 90)", "pet": "str:cat", "empty": "int:"}`

You should write this data schema into cmd like this:

`"{\"date\":\"timestamp:\", \"name\": \"str:rand\", \"type\":\"str:['client', 'partner', 'government']\", 
\"age\": \"int:rand(1, 90)\", \"pet\": \"str:cat\", \"empty\": \"int:\"}"`

You can change default values in `default.ini` file.
