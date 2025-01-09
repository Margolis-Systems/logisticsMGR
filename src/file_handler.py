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


class EXCEL:


    @staticmethod
    def _create_xlsx(file_name, dic):
        import pandas as pd
        df = pd.DataFrame.from_dict(dic)
        df.to_excel(file_name)
        return file_name

    @staticmethod
    def create_xlsx(file_name, dic, headers):
        import xlsxwriter

        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet("My sheet")
        for c in range(len(headers)):
            worksheet.write(0, c, headers[c])
        for r in range(len(dic)):
            for c in range(len(headers)):
                if headers[c] in dic[r]:
                    worksheet.write(r+1, c, dic[r][headers[c]])
        workbook.close()
        return file_name

