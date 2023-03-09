import re
from prettytable import PrettyTable
import datetime



def calculate_age(birthdate, deathdate=None):
    """Calculate age in years given a birthdate and an optional deathdate"""
    birth = datetime.datetime.strptime(birthdate, '%Y-%m-%d')
    if deathdate:
        death = datetime.datetime.strptime(deathdate, '%Y-%m-%d')
        age = (death - birth).days / 365.25
    else:
        age = (datetime.datetime.now() - birth).days / 365.25
    return int(age)



individuals = []
families = []

with open('Family.ged', 'r') as file:
    current_individual = {}
    current_family = {}
 
    for line in file:
        # Extract the level, tag, and value from the line
        match = re.match(r'^(\d+)\s+(@\w+@)?\s*(\w+)?\s*(.*)$', line)
        level = int(match.group(1))
        tag = match.group(3)
        value = match.group(4)

        # Process the line based on its level and tag
        if level == 0:
            # Start of a new record
            if tag == 'INDI':
                # Start of a new individual record
                current_individual = {'id': value}
                individuals.append(current_individual)
            elif tag == 'FAM':
                # Start of a new family record
                current_family = {'id': value}
                families.append(current_family)
        elif level == 1:
            # Information about the current record
            if tag == 'NAME':
                current_individual['name'] = value
            elif tag == 'SEX':
                current_individual['sex'] = value
            elif tag == 'FAMS':
                current_individual.setdefault('spouse_of_families', []).append(value)
            elif tag == 'FAMC':
                current_individual['child_of_family'] = value
            elif tag == 'HUSB':
                current_family['husband_id'] = value
            elif tag == 'WIFE':
                current_family['wife_id'] = value
            elif tag == 'CHIL':
                current_family.setdefault('child_ids', []).append(value)
        elif level == 2:
            # More detailed information about the current record
            if tag == 'DATE':
                current_family['marriage_date'] = value



individual_table = PrettyTable(['ID', 'Name', 'Gender', 'Birthday', 'Age', 'Death'])


for individual in sorted(individuals, key=lambda x: x['id']):
    name = individual['name']
    gender = individual.get('gender', '')
    birth = individual.get('birthdate', '')
    death = individual.get('deathdate', '')
    age = ''
    if birth:
        age = calculate_age(birth, death)
    row = [individual['id'], name, gender, birth, age, death]
    individual_table.add_row(row)


print('Individuals:')
print(individual_table)


family_table = PrettyTable(['ID', 'Husband', 'Wife', 'Children', 'Marriage Date'])


for family in sorted(families, key=lambda x: x['id']):
    husband = next((i.get('name', '') for i in individuals if i['id'] == family.get('husband_id', '')), '')
    wife = next((i.get('name', '') for i in individuals if i['id'] == family.get('wife_id', '')), '')
    children = ', '.join([i.get('name', '') for i in individuals if i['id'] in family.get('child_ids', [])])
    row = [family['id'], husband, wife, children, family.get('marriage_date', '')]
    family_table.add_row(row)

# Print the table
print('Families:')
print(family_table)
