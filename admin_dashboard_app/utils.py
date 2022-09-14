from openpyxl import load_workbook
from admin_dashboard_app.models import Country

read_xlsx = load_workbook(
    '/Users/goddessana/Development/PythonProjects/Django/laboratory_shop_admin_backend/admin_dashboard_app/data_files/Country_code.xlsx')
read_sheet = read_xlsx.active

ids_col = read_sheet['A']
ids = []
for cell in ids_col[1:]:
    ids.append(int(cell.value))
###############################
countrycode_col = read_sheet['B']
country_codes = []
for cell in countrycode_col[1:]:
    country_codes.append(cell.value)
###############################
countrydcode_col = read_sheet['C']
country_dcodes = []
for cell in countrydcode_col[1:]:
    country_dcodes.append(cell.value)
###############################
countryname_col = read_sheet['D']
country_names = []
for cell in countryname_col[1:]:
    country_names.append(cell.value)


def generate_country():
    for i in range(len(ids)):
        print(ids[i], country_codes[i], country_dcodes[i], country_names[i])
        Country(country_char_code=country_codes[i],
                country_tell_code=country_dcodes[i],
                country_name=country_names[i]).save()
