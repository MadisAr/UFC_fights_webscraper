import csv
import difflib
import matplotlib.pyplot as plt

def ask_name(file):
    # Ask input name, get closest match from file
    names = set()
    for row in file:
        names = names | {row[0].lower().capitalize(), row[1].lower().capitalize()}
    while True:
        inp = input()
        try:
            name = difflib.get_close_matches(inp, names)[0]
        except:
            name = ""
        if inp.strip().lower() == name.lower() or name and input(f"Did you mean {name}? (Y/n)") == "Y":
            break
    return name

def main():
    file = open("scraped_stats.csv", "r")
    reader = csv.reader(file)
    name = ask_name(reader)
    file.seek(0)
    elos = [1000]
    dates = []
    for i in reader:
        # print(f"{i[0]},{name}.")
        if str(i[0]).lower() == str(name).lower():
            elos.append(elos[-1] + int(i[3]))
            dates.append(i[2].split(" ")[0])
        elif str(i[1]).lower() == str(name).lower():
            elos.append(elos[-1] - int(i[3]))
            dates.append(i[2].split(" ")[0])
    elos.pop(0)
    plt.plot(dates, elos)
    plt.show()
    
        
if __name__ == "__main__":
    main()