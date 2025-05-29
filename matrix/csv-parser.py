import csv

filename = 'Matrix-Bot/matrix-expired-lists/expired-10-31-23.csv'
Addresses = []

suffixes = ["DR", "RD", "CT", "ST", "AVE", "CIR", "BLVD", "CIR"]

def remove_suffix(text):
    for suffix in suffixes:
        if suffix in text:
            text = text.split(suffix)[0]
    return text

with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        addy = row[3].split(" ")
        addy = [remove_suffix(part) for part in addy]
        combined_address = " ".join(addy)
        Addresses.append(combined_address.strip())

print(Addresses)
