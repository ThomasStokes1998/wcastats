import pandas as pd
import numpy as np
from datetime import date, timedelta

low_memory = False
results = pd.read_csv('WCA Database/WCA_export_Results.tsv', delimiter='\t')
competitions = pd.read_csv('WCA Database/WCA_export_Competitions.tsv', delimiter='\t')
countries = pd.read_csv('WCA Database/WCA_export_Countries.tsv', delimiter='\t')

# Ordering the competition dataframe
def orderComps():
    dates = []
    for i, _ in enumerate(competitions.id):
        y = competitions.year[i]
        m = competitions.month[i]
        d = competitions.day[i]
        dates.append(date(y, m, d))
    competitions["date"] = dates
orderComps()

# results = results[results.best > 0].reset_index(drop="index")
competitions = competitions.sort_values("date").reset_index(drop="index")

continents = {country:countries[countries.id == country].reset_index(drop="index").continentId[0] for country in countries.id}

def main(event: str, soyear: int = 2012 ,places: int=15, startingval: int=1800):
    evres = results[results.eventId == event].reset_index(drop="index")
    idnum = 1
    personinfo = {}
    countryinfo = {}
    times = {}
    dates = {}
    curryear = 2003
    nthplace = startingval
    evres = evres[evres.best < nthplace].reset_index(drop="index")
    # Before ordering comps
    initcomps = competitions[competitions.year < soyear].reset_index(drop="index")
    for i, comp in enumerate(initcomps.id):
        evr = evres[evres.competitionId == comp].reset_index(drop="index")
        if initcomps.date[i].year != curryear:
            evres = evres[evres.best < nthplace].reset_index(drop="index")
            curryear = initcomps.date[i].year
            print(f"Started {curryear}")
        if len(evr) > 0 and i > 0 and min(evr.best) < nthplace:
            for j, b in enumerate(evr.best):
                if 0 < b < nthplace:
                    for k in range(1, 6):
                        if 0 < evr[f"value{k}"][j] < nthplace:
                            personinfo[idnum] = f"{evr.personName[j]}  {evr.personCountryId[j]}  {comp}"
                            countryinfo[idnum] = evr.personCountryId[j]
                            times[idnum] = evr[f"value{k}"][j]
                            dates[idnum] = initcomps.date[i]
                            idnum += 1
                            if len(times) > places:
                                x = np.sort([times[t] for t in times])
                                nthplace = x[places-1]
    # After ordering comps
    print(f"Started ordering competitions. nthplace: {nthplace / 100} .{len(evres)} rows to sort.")
    evres["date"] = evres["competitionId"].apply(lambda x: competitions[competitions.id == x].reset_index(drop="index").date[0])
    evres = evres.sort_values("date").reset_index(drop="index")
    evres = evres[evres.date >= date(soyear, 1, 1)].reset_index(drop="index")
    print("Finished ordering competitions.")
    for i, b in enumerate(evres.best):
        if evres.date[i].year != curryear:
            curryear = evres.date[i].year
            print(f"Started {curryear}")
        if 0 < b < nthplace:
            for k in range(1, 6):
                if 0 < evres[f"value{k}"][i] < nthplace:
                    personinfo[idnum] = f"{evres.personName[i]}  {evres.personCountryId[i]}  {evres.competitionId[i]}"
                    countryinfo[idnum] = evres.personCountryId[i]
                    times[idnum] = evres[f"value{k}"][i]
                    dates[idnum] = evres.date[i]
                    idnum += 1
                    if len(times) > places:
                        x = np.sort([times[t] for t in times])
                        nthplace = x[places-1]

    # Making the dataframe
    df = pd.DataFrame({"name":[personinfo[n] for n in personinfo], "country":[continents[countryinfo[c]] for c in countryinfo]})
    coldate = date(2003, 9, 1)
    print("Started adding rows.")
    while coldate < date.today():
        col = f"{coldate.day}/{coldate.month}/{coldate.year}"
        colvals = []
        for i in times:
            if dates[i] < coldate:
                colvals.append(times[i] / 100)
            else:
                colvals.append(startingval * 2)
        df[col] = colvals
        coldate += timedelta(weeks = 2)
    df.to_csv(f"{event}_results_hist.csv")

if __name__ == "__main__":
    # History of the 15 fastest 333 singles
    main("333")
