import csv
import pprint
import uuid

'''
Diagnosis
Age
Gender

First follo up
Any comobities this pt may have
Question Number     Question        Answer type     Answers     Alert       Next question       Summary

Second Follow up
Question Number     Question        Answer type     Answers     Alert       Next question       Summary

'''

'''
CSV Changes:

Keep - x follo up attached with question
        No other rows in between

Standardize spelling of x follo up
Repeat the same for other csv
'''

base_structure = {
    'disease_id': '',
    'disease_name': '',
    'pathways': {
        'male': [],
        'female': [],
        'others': []
        }
    }

age_map = {
    'infant': {
        'min_age': 0,
        'max_age': 1
        },
    'child (1-5)': {
        'min_age': 1,
        'max_age': 5
        },
    'child (5-12)': {
        'min_age': 5,
        'max_age': 12
        },
    'teenager': {
        'min_age': 13,
        'max_age': 20
        },
    'adult ( 20-40)': {
        'min_age': 20,
        'max_age': 40
        },
    'adult ( 40-60)': {
        'min_age': 40,
        'max_age': 60
        },
    'elderly': {
        'min_age': 60,
        'max_age': 125
        },
    'all': {
        'min_age': 0,
        'max_age': 125
        }
}
gender_options = ['male', 'female', 'others', 'all']


def parse_disease_data(data):
    # Parse data
    disease_name = data[0][1].strip()
    age = data[1][1].strip()
    gender = data[2][1].strip().lower()
    comorbidities = data[3][1].strip()

    return {
        'disease_name': disease_name,
        'age': age,
        'gender': gender,
        'comorbidities': comorbidities
    }


def parse_questions(data):
    question_init = True
    dialogflow = {}
    current_node = {}
    question_count = 1
    rows_used = 0

    for row in data:
        rows_used += 1

        # Skip question header row
        if rows_used == 1:
            continue

        # Check if current row is a new question
        if not question_init:
            try:
                question_number = int(row[0].strip())
            except Exception as e:
                pass
            else:
                # Add current node to flow and create a new node
                dialogflow[str(question_count)] = current_node
                question_count += 1
                current_node = {}
                question_init = True
                # print('New question: ', row)

        # New question - New node
        if question_init:
            # Last question - FOLLO END
            if len(row) == 2:
                question_number, question_end = row
                if question_end == 'FOLLO END':
                    # Create last node
                    current_node['node_id'] = str(question_number)
                    current_node['node_type'] = 'end'
                    current_node['next_node'] = None
                    dialogflow[str(question_count)] = current_node
                    return dialogflow, rows_used
                else:
                    print('==================================================')
                    print('Error in row')
                    print(row)
                    break

            # Check for valid question
            elif len(row) > 7 or len(row) < 5:
                print('==================================================')
                print('Error parsing new question node')
                print(row)
                return

            # Parse valid question
            if len(row) == 5:
                row.insert(3, None)
                row.append(None)
            elif len(row) == 6:
                row.append(None)

            question_init = False
            question_number, question,\
                answer_type, answer, alert,\
                next_question, summary = row

            current_node['node_id'] = str(question_number)
            current_node['node_type'] = 'question'
            current_node['question_data_type'] = 'text'
            current_node['response_type'] = answer_type
            current_node['response_options'] = {
                answer: {
                    'next_node': str(next_question),
                    'alert': alert
                    }
                }
            current_node['next_node'] = None

        # Responses for previous question
        elif 2 < len(row) < 5:
            if len(row) == 3:
                row.append(None)

            answer, alert,\
                next_question, summary = row
            current_node['response_options'][answer] = {
                'next_node': str(next_question),
                'alert': alert
            }

        else:
            print('==================================================')
            print('Error in row')
            print(row)
            break


def parse_pathway(csv_data):
    data_rows = []

    # Clean the data
    for row in csv_data:
        row = [ele for ele in row if ele.strip()]
        if len(row) < 1:
            continue
        # print(row)
        data_rows.append(row)

    if len(data_rows) < 8:
        print('Invalid CSV')
        return
    # print(data_rows)
    disease_data = parse_disease_data(data_rows)
    data_rows = data_rows[4:]
    dialogflows = []

    # Find and extract pathways
    while len(data_rows) > 3:
        row = data_rows.pop(0)
        if len(row) == 2:
            delay_label, delay = row

            if 'follo up' in delay_label.lower():
                delay = int(delay.strip())
                dialgoflow, rows_used = parse_questions(data_rows)
                data_rows = data_rows[rows_used:]
                # pprint.pprint(dialgoflow)
                dialgoflow['dialogflow_id'] = uuid.uuid4().hex
                dialogflows.append({
                    'delay': delay,
                    'dialgoflow': dialgoflow})

    # print('Disease parsed: %s' % disease_data['disease_name'])
    # print('Dialoglfows parsed: %d' % len(dialogflows))
    gender = disease_data['gender'].lower()
    age = disease_data['age'].lower()
    base_structure['disease_name'] = disease_data['disease_name']
    age_range = age_map.get(age, None)

    if gender not in gender_options:
        print('==================================================')
        print('Unable to map gender: %s' % gender)
        return

    if age_range is None:
        print('==================================================')
        print('Unable to map age: ', age)
        return

    pathways = []
    for ele in dialogflows:
        pathways.append({
            'initial_delay': ele['delay'],
            'dialgoflow_id': ele['dialgoflow']['dialogflow_id']
        })
    age_range['dialogflows'] = pathways

    if gender == 'all':
        base_structure['pathways']['male']\
            = base_structure['pathways']['female']\
            = base_structure['pathways']['others']\
            = age_range
    else:
        base_structure['pathways'][gender] = age_range

    pprint.pprint(base_structure)


if __name__ == '__main__':
    with open('pathway.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        parse_pathway(csv_data=reader, delimiter=',')