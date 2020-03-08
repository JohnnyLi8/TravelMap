
import xlrd


class Excel:
    def __init__(self, file_path='trip.xlsx'):
        self.path = file_path
        self.DAYS_COL = 0
        self.DETAILED_ROUTE_COL = 3
        self.TRANSPORTATION_COL = 4
        self.DISTANCE_COL = 5
        self.DURATION_COL = 6
        self.POIS_COL = 7
        self.COUNTRY_ROW = 0
        self.COUNTRY_COL = 1
        self.TRIP_START_ROW = 5
        self.wb = xlrd.open_workbook(self.path)
        self.sheet = self.wb.sheet_by_index(0)
        self.MAX_JUMP = 20  # when locate last col, only check up to next 20 rows
        self.STARTING_ROW = 5
        self.LAST_ROW = self.locate_last_row()

    def get_main_country(self):
        main_country = self.sheet.cell_value(self.COUNTRY_ROW, self.COUNTRY_COL)
        return main_country

    def locate_day(self, day_str):
        col = self.DAYS_COL
        row_runner = self.STARTING_ROW
        cell_val = self.sheet.cell_value(row_runner, col)
        while cell_val != day_str and row_runner < self.LAST_ROW:
            row_runner += 1
            cell_val = self.sheet.cell_value(row_runner, col)
        if row_runner == self.LAST_ROW and day_str != self.sheet.cell_value(self.LAST_ROW, col):
            # print("the trip goes to", self.sheet.cell_value(self.LAST_ROW, col))
            return -1
        # print(day_str + ": row ", row_runner)
        return row_runner

    def locate_last_row(self):
        col = self.DAYS_COL
        last_row_found = False
        row_runner = self.STARTING_ROW
        try:
            while not last_row_found:
                has_values = [(self.sheet.cell_value(row, col) != '')
                              for row in range(row_runner, row_runner+self.MAX_JUMP)]
                # print(has_values)
                if True in has_values:
                    row_runner += next(i for i in reversed(range(len(has_values))) if has_values[i] is True)
                    # print(row_runner)
                else:
                    # print("last row: ", row_runner)
                    return row_runner
        except IndexError:
            # print("last row: row", row_runner)
            return row_runner

    def get_daily_trip(self, day_str):
        day_start_row = self.locate_day(day_str)
        next_day_start_row = self.locate_day(day_str[:-1]+str(int(day_str[-1])+1))
        col = self.DETAILED_ROUTE_COL
        row_runner = day_start_row
        if row_runner == self.LAST_ROW:
            # print("last day: go home")
            return
        cell_runner = self.sheet.cell(row_runner, col)
        daily_trip = []
        while row_runner < next_day_start_row:
            if cell_runner.value is not '':
                daily_trip.append(cell_runner.value)
            row_runner += 1
            cell_runner = self.sheet.cell(row_runner, col)
        # print(routes)
        return daily_trip
