import csv


class CSV:
    @staticmethod
    def create_csv(file_name, dic, headers):
        data = []
        for r in dic:
            new = {}
            for i in r:
                if i in headers:
                    new[i] = r[i]
            data.append(new)
        with open(file_name, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, headers)
            writer.writeheader()
            for r in data:
                writer.writerow(r)
        return file_name
