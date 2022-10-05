import pandas as pd
from datetime import date
import time

results = pd.read_csv('WCA Database/WCA_export_Results.tsv', delimiter='\t')
competitions = pd.read_csv('WCA Database/WCA_export_Competitions.tsv', delimiter='\t')
#persons = pd.read_csv('WCA Database/WCA_export_Persons.tsv', delimiter='\t')
countries_ = pd.read_csv('WCA Database/WCA_export_Countries.tsv', delimiter='\t')

# Order the results dataframe
compdates = {"ongoing":date.today()}
t0 = time.time()
print("Creating the compdates dictionary and ordering the results dataframe.")
for i, comp in enumerate(competitions.id):
    compdates[comp] = date(competitions.year[i], competitions.month[i], competitions.day[i])
results["date"] = results["competitionId"].apply(lambda x: compdates[x])
results = results[results.best > 0].sort_values("date").reset_index(drop="index")
print(f"Time elapsed = {round(time.time()-t0,3)}s")

countries = list(results.personCountryId.unique())
events = list(results.eventId.unique())

continents = {c:countries_.continentId[i] for i, c in enumerate(countries_.id)}

def mbfPoints(p: int, oldstyle: bool=False) -> float:
    if oldstyle:
        tt = p % 100_000
        ss = 199 - p // 10_000_000
        aa = (p // 100_000) % 100
        if tt == 99_999:
            tt = min(600 * aa, 3_600)
        return ss - aa + 1 - tt / 3_600
    else:
        dd = 99 - p // 10_000_000
        mm = p % 100
        tt = (p // 100) % 100_000
        aa = dd + 2 * mm
        if tt == 99_999:
            tt = min(600 * aa, 3_600)
        if aa < 6:
            return dd + 1 - tt / (600 * aa)
        else:
            return dd + 1 - tt / 3_600

def getRank(nr: float, event: str, dateset) -> int:
    r = dateset
    r = r[r.eventId == event].reset_index(drop="index")
    if event == "333mbf":
        r["best"] = r["best"].apply(lambda x: mbfPoints(x, False))
        return 1 + r[r.best > nr].personId.nunique()
    elif event  == "333mbo":
        r["best"] = r["best"].apply(lambda x: mbfPoints(x, True))
        return 1 + r[r.best > nr].personId.nunique()
    else:
        return 1 + r[r.best < nr].personId.nunique()

def getEventPop(dateset) -> dict:
    r = dateset
    eventnums = {}
    for event in events:
        e = r[r.eventId == event]
        eventnums[event] = e.personId.nunique()
    return eventnums

def formatTime(t: float, prec: int = 0):
    h = round(t // 3600)
    t_h = t - 3600 * h
    m = round(t_h // 60)
    t_h_m = t_h - 60 * m
    if prec == 0:
        s = round(t_h_m)
    else:
        s = round(t_h_m, prec)
    if m < 10:
        if s < 10:
            return f"{h}:0{m}:0{s}"
        else:
            return f"{h}:0{m}:{s}"
    elif s < 10:
        return f"{h}:{m}:0{s}"
    else:
        return f"{h}:{m}:{s}"

def main(loadsave: bool=True):
    if loadsave:
        print("Loading in data")
        df = pd.read_csv("countrysorhist.csv")     
        dfdict = {}
        for col in list(df.columns):
            dfdict[col] = list(df[col])
        m, y= col.split("/")
        smonth = date(int(y), int(m), 1)
        print("Loaded data, last month detected: "+col)
    else:
        dfdict = {"country":[c for c in countries], "continent":[continents[c] for c in countries]}
        countrynrs = {c:{event:-1 for event in events} for c in countries}
    t0 = time.time()
    countrynrs = {c:{event:-1 for event in events} for c in countries}
    retired_events = []
    for i, d in enumerate(results.date):
        if i > 0 and results.date[i-1].year > 2002 and (d.month != results.date[i-1].month or d.year != results.date[i-1].year):
            d_ = results.date[i-1]
            if loadsave and d.year > d_.year >= smonth.year:
                print(f"Finished {d_.year}. Time elapsed = {formatTime(time.time()-t0)}")
            # Remove events no longer in WCA from the SOR calculation
            if d.year == 2009 and d_.year == 2008:
                retired_events.append("333mbo")
            elif d.year == 2014 and d_.year == 2013:
                retired_events.append("magic")
                retired_events.append("mmagic")
            elif d.year == 2020 and d_.year == 2019:
                retired_events.append("333ft")
            # Start from the last save point
            if not loadsave or loadsave and (d_.year > smonth.year or d_.year == smonth.year and d_.month > smonth.month):
                eventnums = getEventPop(results[:i])
                dateindex = f"{d_.month}/{d_.year}"
                if d_.month < 10:
                    dateindex = "0" + dateindex
                csor= []
                for c in countries:
                    sor = 0
                    for event in events:
                        if eventnums[event] > 0 and event not in retired_events:
                            nr = countrynrs[c][event]
                            if nr == -1:
                                sor += eventnums[event]
                            else:
                                sor += getRank(nr, event, results[:i])
                    csor.append(sor)
                print(f"Finished SOR for {dateindex}. Time elapsed = {formatTime(time.time()-t0)}")
                    
                dfdict[dateindex] = csor
                df = pd.DataFrame(dfdict)
                df.to_csv("countrysorhist.csv", index=False)
        b, ev, co = results.best[i], results.eventId[i], results.personCountryId[i]
        n = countrynrs[co][ev]
        # Check if a new NR has been set
        if n == -1:
            if ev == "333mbf":
                countrynrs[co][ev] = mbfPoints(b)
            elif ev == "333mbo":
                countrynrs[co][ev] = mbfPoints(b, True)
            else:
                countrynrs[co][ev] = b
        elif ev == "333mbf":
            if n < mbfPoints(b):
                countrynrs[co][ev] = mbfPoints(b)
        elif ev == "333mbo":
            if n < mbfPoints(b, True):
                countrynrs[co][ev] = mbfPoints(b, True)
        elif b < n:
            countrynrs[co][ev] = b
    return

if __name__ == "__main__":
    # Country SOR History (Singles)
    main()
