
from Excel import Excel
import os.path


class Trip:
    def __init__(self):
        self.routes = {}
        self.excel = Excel()
        self.TRIP_DAYS = int(self.excel.sheet.cell_value(self.excel.LAST_ROW,
                                                        self.excel.DAYS_COL).split(" ")[-1])
        self.waypoints = self.get_trip_waypoints()
        self.main_country = self.excel.get_main_country()
        create_user_folder()

    def get_trip_waypoints(self):
        for i in range(1, self.TRIP_DAYS+1):
            day_str = "Day " + str(i)
            self.routes[day_str] = self.get_daily_waypoints(day_str)
        # print(self.routes)
        return self.routes

    def get_daily_waypoints(self, day_str):
        daily_trip = self.excel.get_daily_trip(day_str)
        if daily_trip is None:
            return ["go home"]  # be careful of type of return
        waypoints = []
        for route in daily_trip:
            # print(route)
            if route == "Optional below:":
                break
            info = route.split(" - ")
            if len(info) == 2:
                origin = info[0]
                desti = info[1]
                if waypoints:
                    if waypoints[-1] == origin or waypoints[-1].split(", ")[0] == origin:
                        # in case E.g.: Como, Italy -> Como in the following entries
                        waypoints.append(desti)
                    else:
                        waypoints.append(origin)
                        waypoints.append(desti)
                else:
                    waypoints.append(origin)
                    waypoints.append(desti)
            elif len(info) > 2:
                [waypoints.append(info[i]) for i in range(1, len(info))]
        # print(waypoints)
        return waypoints


def create_user_folder():
    if not os.path.exists('user'):
        os.mkdir('user')
        print('user folder created')
    if not os.path.exists('maps'):
        os.mkdir('maps')
        print('maps folder created')
