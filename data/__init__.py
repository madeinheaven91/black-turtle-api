import csv


groups_csv = {}
with open("data/groups.csv", "r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        group_name = row["name"]
        group_id = row["id"]
        groups_csv[group_name] = group_id

with open("data/teachers.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    teachers_csv = list(csv_reader)
teachers_csv = teachers_csv
