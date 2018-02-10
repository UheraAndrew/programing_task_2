from collections import defaultdict
import requests
import folium
import time


def line_devision(s):
    """
    str -> tuple
    This function returns name, year, country of film from the line, and group
    """

    d = -1
    for i in range(len(s) - 5):
        if (s[i] == '(') and (s[i + 5] in ')/'):
            d = i + 1
            temp = s[d:d + 4]
            try:
                if temp != "????":
                    int(temp)
            except ValueError:
                continue
            break
    name = s[0:d - 1]
    date = s[d:d + 4]

    if s[-1] != ')':
        end = s.rfind("\t") + 1
        place = s[end:]
        type_f = "-"
    else:
        end = s.rfind("\t")
        start = s.rfind("\t", 0, end) + 1
        place = s[start:end]
        type_f = s[end + 1:]
    return name, date, place, type_f


def read_file(path, year):
    """
    (str) -> list
    Return list of lines from file (path to file)
    """
    slovn = defaultdict(lambda: defaultdict(list))

    with open(path, "r", errors="ignore", encoding="UTF-8") as file_input:
        input_lines = file_input.readlines()

    for i in range(14, len(input_lines) - 1):
        temp = line_devision(input_lines[i].strip())
        if temp[1] == year:
            slovn[temp[2]][temp[3]].append(temp[0])

    return slovn


def get_cordinates(place, user_interface=False):
    """
    (str) -> int, int

    This function return geo cordinates of place which is in input address
    if cordinates not found return None, None
    """

    try:
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'sensor': 'false', 'address': place,
                  'key': "AIzaSyCyMdmIKMY7ec8qCkOZs5chaWOeVW9jJUM"
                  }
        r = requests.get(url, params=params)
        time.sleep(0.0005)
        results = r.json()['results']
        location = results[0]['geometry']['location']
        return location['lat'], location['lng']
    except IndexError:
        return None, None
    except requests.exceptions.ConnectionError as con_er:
        if user_interface:
            print(con_er)
            print("progress bar fell")
            while True:
                answer = input("\nTry again?[y/N]")
                if answer == "y":
                    print("wait three seconds")
                    time.sleep(3)
                    return get_cordinates(place)
                elif answer == "N":
                    return None, None
                else:
                    continue
        else:
            print(con_er)
            print("the program ends unsuccessful ")
            exit(0)


def create_map(data, name="Map", user_interface=False):
    """
    dict, name = "Map", user_interface = False -> None

    This function gets dict in which key is address and value is
    another dict in which key is name for group and value is list
    of films names

    {address:  {group_name:[film1, film2, ...]} }
    """

    map_out = folium.Map(location=[49.817545, 24.023932], zoom_start=17)

    fg1 = folium.FeatureGroup(name="studio")
    fg2 = folium.FeatureGroup(name="location")
    fg3 = folium.FeatureGroup(name="unknown")
    fg4 = folium.FeatureGroup(name="others")
    if user_interface:
        num = len(data.keys())
        print("Creating the map process\n" +
              " 0% |   |   |   |20%|   |   |   |   |40%|   |" +
              "   |   |60%|   |   |   |80%|   |   |   |100%\n    |",
              end="",
              flush=True)
        count1 = 0
        step = 1 / num
        progres = 0.0
        not_found = 0

    for temp in data:

        lt, ln = get_cordinates(temp, user_interface=True)
        if user_interface:
            count1 += step
            if count1 >= progres:
                for i in range(0, int((count1 - progres) // 0.0125)):
                    print("", end="|", flush=True)
                progres += ((count1 - progres) // 0.0125) * 0.0125

        if lt is None:
            not_found += 1
            continue

        for i in data[temp]:

            if i == "-":
                out_str = ""
                count = 1
                for j in data[temp][i]:
                    out_str += "({}.{}) ".format(count, j)
                    count += 1

                fg1.add_child(folium.CircleMarker(location=[lt, ln],
                                                  popup=out_str.replace(
                                                      "'", "`"),
                                                  radius=5,
                                                  color="grey",
                                                  fill_color="grey",
                                                  fill_opacity=0.5))
            elif i == "(studio)":
                out_str = ""
                count = 1
                for j in data[temp][i]:
                    out_str += "({}.{}) ".format(count, j)
                    count += 1
                fg2.add_child(folium.CircleMarker(location=[lt, ln],
                                                  popup=out_str.replace(
                                                      "'", "`"),
                                                  radius=5,
                                                  color="red",
                                                  fill_color="red",
                                                  fill_opacity=0.5))
            elif i.endswith("location)"):
                out_str = ""
                count = 1
                for j in data[temp][i]:
                    out_str += "({}.{}) ".format(count, j)
                    count += 1
                fg3.add_child(folium.CircleMarker(location=[lt, ln],
                                                  popup=out_str.replace(
                                                      "'", "`"),
                                                  radius=5,
                                                  color="yellow",
                                                  fill_color="yellow",
                                                  fill_opacity=0.5))
            else:
                out_str = ""
                count = 1
                for j in data[temp][i]:
                    out_str += "({}.{}) ".format(count, j)
                    count += 1

                fg4.add_child(folium.CircleMarker(location=[lt, ln],
                                                  popup=out_str.replace(
                                                      "'", "`"),
                                                  radius=5,
                                                  color="green",
                                                  fill_color="green",
                                                  fill_opacity=0.5
                                                  ))

    map_out.add_child(fg1)
    map_out.add_child(fg2)
    map_out.add_child(fg3)
    map_out.add_child(fg4)
    map_out.add_child(folium.LayerControl())
    map_out.save(name + '.html')

    if user_interface:
        print("\nAll places ", num)
        print("There are not found places", not_found)
        print("\nDone\nFile saved to ", name + ".html")


def main():
    """
    This function provide user interface
    :return:
    """
    year = input("Please, input year in this format ####\nwhere # is digit\n")
    print("Get data from file")
    temp = read_file("locations.list", year)
    print("Done\n")

    create_map(temp, user_interface=True)


main()
