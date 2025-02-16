# create a mapping of state to abbreviation
states = {
    "Oregon" : "OR",
    "Florida" : "FL",
    "California" : "CA",
    "New York" : "NY",
    "Michigan" : "MI" 
}

# create a basic set of states and some cities in them
cities = {
    "CA" : "San Francisco",
    "MI" : "Detroit",
    "FL" : "Jacksonville"
}

# add some more cities
cities['NY'] = "New York"
cities["OR"] = "Portland"

# print out some cities
print('-' * 10)
print("NY State has: ", cities["NY"])
print("Or State has: ", cities["OR"])

# print out some states
print('-' * 10)
print("Michigan's abbreviation is: ", states["Michigan"])
print("Florida's abbreivation is: ", states["Florida"])

# do it by using the state then cities dict
print('-' * 10)
print("Michigan has: ", cities[states["Michigan"]])
print("Flordia has: ", cities[states["Florida"]])

# print every state abbreviation
print('-' * 10)
for state, abbrev in list(states.items()):
    print(f"{state} is abbreviated {abbrev}")

# print every city in state
print('-' * 10)
for abbrev, city in list(cities.items()):
    print(f"{abbrev} has the city {city}")

# print every city in state
print('-' * 10)
for state, abbrev in list(states.items()):
    print(f"{state} state is abbreviated {abbrev}")
    print(f"and has city {cities[abbrev]}")

print('-' * 10)
# now do both at the same time
state = states.get('Texas')

if not state:
    print("Sorry, no Texas")

# get a city with a default value
city = cities.get("TX", "Does Not Exist")
print(f"The city for state 'Tx' is: {city}" )