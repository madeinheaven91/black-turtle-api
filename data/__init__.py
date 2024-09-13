import csv


with open("data/groups.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    groups_csv = list(csv_reader)
groups_csv = groups_csv

with open("data/teachers.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    teachers_csv = list(csv_reader)
teachers_csv = teachers_csv
